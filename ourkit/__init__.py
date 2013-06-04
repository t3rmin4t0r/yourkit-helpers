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
		self.parent = parent
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
			return 1			
		time = intparse(node.attributes["time_ms"])
		own_time = intparse(node.attributes["own_time_ms"])
		count = intparse(node.attributes["invocation_count"])
		name = node.attributes["name"].value
		call = Call(parent, name, time, own_time, count)			
		call.children = [self.parse(child, call) for child in node.childNodes if child.nodeName == "node"]			
		return call

class PStatsAdapter(object):	
	def __init__(self, thread):
		if type(thread) != Call:
			raise "Wrong type for PStatsAdapter: " + type(thread) + " expected " + Call
		self.stats = {}
		self.thread = thread
	"""
		{('~', 0, 'func') : (cc, nc, tt, ct, 
			{"caller" : (cc, nc, tt, ct), }
		cc = primary calls
		nc = total calls (cc + recursion)
		tt = own time
		ct = time
	"""
	def create_stats(self):
		if(not self.stats):
			self.finagle(self.thread, set())
	def finagle(self, call, parents):
		func = ('~', 0, call.name)
		# this is why I like python !
		vadd = lambda a,b: tuple([(i+j) for i,j in zip(list(a), list(b))])
		if(not self.stats.has_key(func)):
			self.stats[func] = (0,0,0.0,0.0, {})
		(cc,nc,tt,ct, callers) = self.stats[func]
		_cc,_nc,_tt,_ct = (0,0,0.0,0.0)

		if(not (call.name in parents)):
			_cc = call.count
			_ct = call.time/1000.0
		_nc = call.count
		_tt = call.own_time/1000.0
		old = (cc, nc, tt, ct)		
		item = (_cc, _nc, _tt, _ct)
		if(call.parent): 
			parent = ('~', 0, call.parent.name)
			if(not callers.has_key(parent)):
				callers[parent] = (0,0,0.0,0.0)
			callers[parent] = vadd(callers[parent], item)
		# yeah, + is tuple concat not vector addition
		self.stats[func] = vadd(old, item)+(callers,)
		parents = parents | set([call.name])
		for child in call.children:	
			self.finagle(child, parents)

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
