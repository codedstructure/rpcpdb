#!/usr/bin/python2.5 -u

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn

import time
# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Threaded mix-in
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# Create server
server = ThreadedXMLRPCServer(("localhost", 8000),
                            requestHandler=RequestHandler,
                            allow_none=True)
server.register_introspection_functions()

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'div').
import updb

import sys
class MyFuncs(updb.UPdb_mixin):
    def add(self, x, y):
        return x+y
    def pow(self, x, y):
	    return pow(x,y)
    def div(self, x, y):
        return x // y

    def slowprint(self, s):
        for c in s:
            sys.stdout.write(c)
            time.sleep(0.25)
        sys.stdout.write('\n')

    def longrun(self):
        while 1:
          time.sleep(0.5)

server.register_instance(MyFuncs())
# Run the server's main loop
server.serve_forever()
