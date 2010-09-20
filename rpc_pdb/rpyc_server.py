#!/usr/bin/python2.5 -u

import time
import rpyc

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'div').
import updb

class RpycUPdb_mixin(updb.UPdb_mixin):
    def exposed_debug_func(self, f, *o, **k):
        return self.debug_func(f, *o, **k)
    def exposed_undebug_func(self, f):
        return self.undebug_func(f)

import sys
class MyFuncs(RpycUPdb_mixin, rpyc.Service):
    def on_connect(self):
        # code that runs when a connection is created (to init the serivce, if needed)
        pass
 
    def on_disconnect(self):
        # code that runs when the connection has already closed (to finalize the service, if needed)
        pass

    def exposed_add(self, x, y):
        return x+y
    def exposed_pow(self, x, y):
	    return pow(x,y)
    def exposed_div(self, x, y):
        return x // y

    def exposed_slowprint(self, s):
        for c in s:
            sys.stdout.write(c)
            time.sleep(0.25)
        sys.stdout.write('\n')

    def exposed_longrun(self):
        while 1:
          time.sleep(0.5)


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyFuncs, port = 18861)
    t.start()
