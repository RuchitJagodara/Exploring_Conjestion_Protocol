#!/usr/bin/env python3
import argparse
import time
import os
import sys
import threading

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
# import cli
from mininet.cli import CLI

# Define a custom topology that builds the network based on the experiment option.
class CustomTopo(Topo):
    def __init__(self, option='a', scenario=None, loss=0, **opts):
        # Save experiment parameters as instance variables.
        self.option = option
        self.scenario = scenario
        self.loss = loss
        # Call the parent constructor; this triggers build().
        super().__init__(**opts)

    def build(self):
        option = self.option
        scenario = self.scenario
        loss = self.loss

        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        
        if option in ['a', 'b']:
            # For experiments a and b: basic topology.
            self.addLink(h1, s1)
            self.addLink(h2, s1)
            self.addLink(h3, s2)
            self.addLink(h4, s3)
            self.addLink(h5, s3)
            self.addLink(h6, s4)
            self.addLink(h7, s4)
            self.addLink(s1, s2)
            self.addLink(s2, s3)
            self.addLink(s3, s4)
        elif option == 'c':
            # For experiment c: use TCLink to set bandwidth and loss.
            self.addLink(h1, s1)
            self.addLink(h2, s1)
            self.addLink(h3, s2)
            self.addLink(h4, s3)
            self.addLink(h5, s3)
            self.addLink(h6, s4)
            self.addLink(h7, s4)
            self.addLink(s1, s2, cls=TCLink, bw=100, use_htb=True,
                         max_queue_size=1000, tcopts='htb default 1 r2q 1')
            self.addLink(s2, s3, cls=TCLink, bw=50, loss=loss, use_htb=True,
                         max_queue_size=1000, tcopts='htb default 1 r2q 1')
            self.addLink(s3, s4, cls=TCLink, bw=100, use_htb=True,
                         max_queue_size=1000, tcopts='htb default 1 r2q 1')


# Experiment (a): Single flow (client on H1, server on H7).
def run_experiment_a(net, cc_scheme):
    h7.cmd('iperf3 -s -D')
    time.sleep(2)
    info('*** Running iperf3 client on h1\n')
    result = h1.cmd('iperf3 -c ' + h7.IP() +
                    ' -p 5201 -b 10M -P 10 -t 150 -C ' + cc_scheme)
    info(result)

# Experiment (b): Three flows from H1, H3, and H4 with staggered start times.
def run_experiment_b(net, cc_scheme):
    h1 = net.get('h1')
    h3 = net.get('h3')
    h4 = net.get('h4')
    h7 = net.get('h7')
    info('*** Starting iperf3 server on h7\n')
    h7.cmd('iperf3 -s -D -p 5201')
    h7.cmd('iperf3 -s -D -p 5202')
    h7.cmd('iperf3 -s -D -p 5203')
    time.sleep(2)
    
    def client_flow(host, start_delay, duration, port):
        time.sleep(start_delay)
        info('*** {} starting client for {} seconds\n'.format(host.name, duration))
        result = host.cmd('iperf3 -c ' + h7.IP() +
                           ' -p {} -b 10M -P 10 -t {} -C {}'.format(port, duration, cc_scheme))
        info('*** {} flow finished\n'.format(host.name))
        info(result)

    threads = []
    threads.append(threading.Thread(target=client_flow, args=(h1, 0, 150, 5201)))
    threads.append(threading.Thread(target=client_flow, args=(h3, 15, 120, 5202)))
    threads.append(threading.Thread(target=client_flow, args=(h4, 30, 90, 5203)))
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()

# Experiment (c): Bandwidth-limited topology with extra links.
def run_experiment_c(net, cc_scheme, scenario):
    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')
    h7 = net.get('h7')
    info('*** Starting iperf3 server on h7\n')
    h7.cmd('iperf3 -s -D')
    time.sleep(2)

    if scenario == 'c1':
        info('*** Running iperf3 client on h3\n')
        result = h3.cmd('iperf3 -c ' + h7.IP() +
                        ' -p 5201 -b 10M -P 10 -t 150 -C ' + cc_scheme)
        info(result)
    elif scenario == 'c2a':
        def client_flow(host):
            result = host.cmd('iperf3 -c ' + h7.IP() +
                              ' -p 5201 -b 10M -P 10 -t 150 -C ' + cc_scheme)
            info(result)
        t1 = threading.Thread(target=client_flow, args=(h1,))
        t2 = threading.Thread(target=client_flow, args=(h2,))
        t1.start(); t2.start()
        t1.join(); t2.join()
    elif scenario == 'c2b':
        def client_flow(host):
            result = host.cmd('iperf3 -c ' + h7.IP() +
                              ' -p 5201 -b 10M -P 10 -t 150 -C ' + cc_scheme)
            info(result)
        t1 = threading.Thread(target=client_flow, args=(h1,))
        t3 = threading.Thread(target=client_flow, args=(h3,))
        t1.start(); t3.start()
        t1.join(); t3.join()
    elif scenario in ['c2c', 'c2d']:
        def client_flow(host):
            result = host.cmd('iperf3 -c ' + h7.IP() +
                              ' -p 5201 -b 10M -P 10 -t 150 -C ' + cc_scheme)
            info(result)
        t1 = threading.Thread(target=client_flow, args=(h1,))
        t3 = threading.Thread(target=client_flow, args=(h3,))
        t4 = threading.Thread(target=client_flow, args=(h4,))
        t1.start(); t3.start(); t4.start()
        t1.join(); t3.join(); t4.join()

if __name__ == '__main__':
    setLogLevel('info')
    
    parser = argparse.ArgumentParser(description='Mininet TCP Congestion Control Experiments')
    parser.add_argument('--option', choices=['a', 'b', 'c'], required=True,
                        help='Experiment option: a, b, or c')
    parser.add_argument('--cc', choices=['bic', 'highspeed', 'yeah'], default='bic',
                        help='TCP Congestion Control scheme')
    parser.add_argument('--scenario', choices=['c1', 'c2a', 'c2b', 'c2c', 'c2d'],
                        help='Experiment c scenario (required for option c)')
    parser.add_argument('--loss', type=int, default=0,
                        help='Link loss percentage for link S2-S3 (only for experiment c)')
    args = parser.parse_args()
    
    # Clean up any leftover Mininet state.
    os.system('mn -c')
    
    if args.option in ['a', 'b']:
        topo = CustomTopo(option=args.option, scenario=None, loss=0)
    elif args.option == 'c':
        if not args.scenario:
            print("For experiment c, please specify --scenario")
            sys.exit(1)
        topo = CustomTopo(option='c', scenario=args.scenario, loss=args.loss)
    
    # Create the network without any controller.
    net = Mininet(topo=topo, controller=None, link=TCLink)

    CLI(net)
    net.start()
    
    
    # With no controller, force switches to operate in standalone mode (learning switch behavior).
    for sw in net.switches:
        sw.cmd('ovs-vsctl set-fail-mode {} standalone'.format(sw.name))

    time.sleep(10)
    
    # Run the experiment based on the option.
    if args.option == 'a':
        run_experiment_a(net, args.cc)
    elif args.option == 'b':
        run_experiment_b(net, args.cc)
    elif args.option == 'c':
        run_experiment_c(net, args.cc, args.scenario)
    

    CLI(net)
    net.stop()
