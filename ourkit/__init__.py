import sys,re,os,math
# to generate XML file
# java -Dexport.xml -Dexport.call.tree.cpu -jar /opt/yourkit/lib/yjp.jar -export $i .
# 
class Call(object):
	def __init__(self, parent, name, time, own_time, count):
		self.name = name
		self.children = []
		self.time = time
		self.own_time = own_time
		self.count = count
	def __repr__(self):
		return "<'%s', time=%d>" % (self.name,self.time)

class CallProfile(object):
	def __init__(self, f):
		from xml.dom import minidom
		self.threads = []
		self.xmldoc = minidom.parse(f)
		self.parsed = False
	def walk(self, node=None):
		if(self.parsed): return
		if(node == None): node = self.xmldoc
		for child in node.childNodes:
			if(child.nodeName == "node"):
				self.threads.append(self.parse(child))
			else:
				self.walk(child)
		if(node == self.xmldoc): 
			self.parsed = True
			del self.xmldoc
		
	def parse(self, node, parent=None):
		call = None
		def intparse(a):
			x = a.value
			if(x): return int(x)
			return 0
		time = intparse(node.attributes["time_ms"])
		own_time = intparse(node.attributes["own_time_ms"])
		count = intparse(node.attributes["invocation_count"])
		name = node.attributes["name"].value
		call = Call(parent, name, time, own_time, count)			
		call.children = [self.parse(child, call) for child in node.childNodes if child.nodeName == "node"]			
		return call

def expensive(root, key=lambda c: c.time):
	ret = [root]
	while root.children:
		root = max(root.children, key=key)
		ret.append(root)
	return ret

def main(args):
	for f in args:
		p = CallProfile(f)
		p.walk()		
		longest = max(p.threads, key=lambda c: c.time)
		calltree = expensive(longest)
		print f
		print "\n".join(["%s %s %d ms/%d" % (i*' ',n.name,n.time,n.count) for (i,n) in enumerate(calltree)])

if __name__ == "__main__":
	main(sys.argv[1:])
