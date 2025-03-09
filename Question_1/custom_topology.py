from mininet.topo import Topo

class MyTopo( Topo ):
	def build(self):

		# Add hosts
		H1 = self.addHost('H1')
		H2 = self.addHost('H2')
		H3 = self.addHost('H3')
		H4 = self.addHost('H4')
		H5 = self.addHost('H5')
		H6 = self.addHost('H6')
		H7 = self.addHost('H7')

		# Add switches
		S1 = self.addSwitch('S1')
		S2 = self.addSwitch('S2')
		S3 = self.addSwitch('S3')
		S4 = self.addSwitch('S4')

		# Add links
		self.addLink(H1, S1)
		self.addLink(H2, S1)

		self.addLink(S1, S2)
		self.addLink(H3, S2)

		self.addLink(S2, S3)

		self.addLink(H4, S3)
		self.addLink(H5, S3)

		self.addLink(S3, S4)

		self.addLink(H6, S4)
		self.addLink(H7, S4)

topos = { 'mytopo': ( lambda: MyTopo() ) }