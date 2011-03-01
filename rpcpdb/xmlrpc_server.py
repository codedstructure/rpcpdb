#!/usr/bin/env python -u

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn

import time
# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Threaded mix-in
class ThreadedXMLRPCServer(ThreadingMixIn,
                           SimpleXMLRPCServer):
    pass

# Create server
server = ThreadedXMLRPCServer(("localhost", 8000),
                              requestHandler=RequestHandler,
                              allow_none=True)
server.register_introspection_functions()


class RpcServer(object):
    def next_prime(self, p):
        """
        Naive, flaky and slow way to get the next
        prime number after that given.
        """
        if p < 2:
            # return first prime: 2
            return 2
        i = p  # start where we left off
        while True:
            i += 1
            probe = 2
            while True:
                if i % probe == 0:
                    # i is composite
                    break
                if probe >= p:
                    # i is co-prime to integers up to p.
                    return i
                probe += 1

if __debug__:
    import updb
    class DebuggableRpcServer(RpcServer, updb.UPdb_mixin):
        pass

    server_instance = DebuggableRpcServer()
else:
    server_instance = RpcServer()

server.register_instance(server_instance)
# Run the server's main loop
server.serve_forever()
