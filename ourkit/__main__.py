from ourkit import CallProfile

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
	import sys
	main(sys.argv[1:])
