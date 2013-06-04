Helpers for Yourkit Profiler
============================

When you run [yourkit](http://yourkit.com) with hadoop, you end up with a few hundred map-tasks and their individual outputs.

If you're like me, you have no clue which one is the slow one from the 168 map-tasks you have distributed across 20 machines.

This is a quick-n-dirty way to churn through them to find the candidate file you're looking for.

	$ ./convert-yjp.sh /grid/0/yjp/YarnChild-2013-05-10-shutdown-26.snapshot
	$ python -m ourkit YarnChild-2013-05-10-shutdown-26-Call-tree-by-thread.xml
	
	YarnChild-2013-05-10-shutdown-26-Call-tree-by-thread.xml
	 main native ID: 0x2AA group: 'main' 381447 ms/0
	  org.apache.hadoop.mapred.YarnChild.main(String[]) 381049 ms/1
	   org.apache.hadoop.security.UserGroupInformation.doAs(PrivilegedExceptionAction) 375170 ms/2
	    javax.security.auth.Subject.doAs(Subject, PrivilegedExceptionAction) 375170 ms/2
	     org.apache.hadoop.mapred.YarnChild$2.run() 375068 ms/1
	      org.apache.hadoop.mapred.MapTask.run(JobConf, TaskUmbilicalProtocol) 374313 ms/1
	       org.apache.hadoop.mapred.MapTask.runOldMapper(JobConf, JobSplit$TaskSplitIndex, TaskUmbilicalProtocol, Task$TaskReporter) 374145 ms/1
	        org.apache.hadoop.mapred.MapRunner.run(RecordReader, OutputCollector, Reporter) 357579 ms/1
	         org.apache.hadoop.hive.ql.exec.ExecMapper.close() 348795 ms/1
	          org.apache.hadoop.hive.ql.exec.Operator.close(boolean) 348788 ms/1
	           org.apache.hadoop.hive.ql.exec.Operator.close(boolean) 348788 ms/1
	            org.apache.hadoop.hive.ql.exec.Operator.close(boolean) 348787 ms/1
	             org.apache.hadoop.hive.ql.exec.SMBMapJoinOperator.closeOp(boolean) 348786 ms/1
	              org.apache.hadoop.hive.ql.exec.SMBMapJoinOperator.joinFinalLeftData() 348786 ms/1
	
By default, it prints out the most expensive call-tree in the code. 

Apply liberally with xargs -n 1 for immediate results, instead of downloading them all for no good reason.

This is probably the simplest thing you can do with the script, but if you wanted to dig deeper, the `ourkit/__init.py` has very little code and needs no docs (if you think otherwise, please fork and send a pull-request).

Just for fun, I've written a python pstats compatible dumper, which can dump each thread out in pstats

	import ourkit, sys, pstats
	p = ourkit.CallProfile(sys.argv[1])
	p.walk()
	longest = max(p.threads, key=lambda c: c.time)
	stats = pstats.Stats(ourkit.PStatsAdapter(longest))
	stats.sort_stats('cumulative').print_stats(10)
	

