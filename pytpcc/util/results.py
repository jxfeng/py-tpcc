# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# Copyright (C) 2011
# Andy Pavlo
# http://www.cs.brown.edu/~pavlo/
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------

import logging
from datetime import datetime

class Results:
    
    def __init__(self, handle):
        self.handle = handle
        self.start = None
        self.stop = None
        self.txn_id = 0
        
        self.txn_counters = { }
        self.txn_times = { }
        self.running = { }
        
    def startBenchmark(self):
        """Mark the benchmark as having been started"""
        assert self.start == None
        logging.debug("Starting benchmark statistics collection")
        self.start = datetime.now()
        return self.start
        
    def stopBenchmark(self):
        """Mark the benchmark as having been stopped"""
        assert self.start != None
        assert self.stop == None
        logging.debug("Stopping benchmark statistics collection")
        self.stop = datetime.now()
        
    def startTransaction(self, txn):
        self.txn_id += 1
        id = self.txn_id
        self.running[id] = (txn, datetime.now())
        return id
        
    def stopTransaction(self, id):
        """Record that the benchmark completed an invocation of the given transaction"""
        assert id in self.running
        txn_name, txn_start = self.running[id]
        del self.running[id]
        
        duration = (datetime.now() - txn_start).microseconds
        total_time = self.txn_times.get(txn_name, 0)
        self.txn_times[txn_name] = total_time + duration
        
        total_cnt = self.txn_counters.get(txn_name, 0)
        self.txn_counters[txn_name] = total_cnt + 1
    
    def __str__(self):
        if self.start == None:
            return "Benchmark not started"
        if self.stop == None:
            duration = (datetime.now() - self.start).seconds
        else:
            duration = (self.stop - self.start).seconds
        
        col_width = 16
        total_width = (col_width*4)+2
        f = "\n  " + (("%-" + str(col_width) + "s")*4)
        
        ret = u"%s Results after %d seconds\n%s" % (str(self.handle).title(), duration, "-"*total_width)
        ret += f % ("", "Executed", u"Time (µs)", "Rate")
        
        total_time = 0
        total_cnt = 0
        for txn in sorted(self.txn_counters.keys()):
            txn_time = self.txn_times[txn]
            txn_cnt = self.txn_counters[txn]
            rate = u"%.02f txn/s" % ((txn_time / txn_cnt) / 1000000.0)
            ret += f % (txn, str(txn_cnt), str(txn_time), rate)
            
            total_time += txn_time
            total_cnt += txn_cnt
        ret += "\n" + ("-"*total_width)
        total_rate = "%.02f txn/s" % ((total_time / txn_cnt) / 1000000.0)
        ret += f % ("TOTAL", str(total_cnt), str(total_time), total_rate)

        return (ret.encode('utf-8'))
## CLASS