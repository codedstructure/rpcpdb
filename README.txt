rpcpdb
======

A PDB wrapper designed to be part of RPC systems for remote
introspection and debugging of RPC server state

Features
--------
 * debug any API function from the client side
 * open an interactive console into the RPC process
 * match and ignore count on function breakpoints
 * Python 2 and 3 support

About
-----
rpcpdb is a wrapper around the Python pdb debugger which
makes it more suitable for use in RPC contexts.
It also provides a similar interface to a code.InteractiveConsole
instance within the context of the target RPC process.

It is designed to fulfil the need to debug a function on
an already-running server which uses threads or processes
to dispatch each remote procedure call, without having to
change the source code to the server in any way. There is
no disruption to other clients and rpc calls while the
selected call is being debugged.

In particular, a mixin class is provided which adds the
`debug_func` and `undebug_func` methods to your RPC server.
These allow breakpoints to be controlled by another RPC
client.

For an example, run the xmlrpc_server.py server process,
then run one or more xmlrpc_client.py processes which will
continually perform RPC requests against it. xmlrpc_debug.py
can then be run to inject a debug breakpoint in a method
which the clients are continually calling; the next client
to call that function will be remotely debuggable, while
other clients carry on oblivious.

An alternative example added in v0.2 is the 'test_server.py'
which does not use RPC but runs functions in background threads.
It gives a good overview of usage in a single module without
extra dependencies.

Currently the debug interface is provided via a UNIX socket,
but this will be extended in future.

RPC framework support is intended to cover XMLRPC, RPyC and
Pyro in the initial stages.

Plans
-----

 * Update examples, tidy up, document.
 * Support other interfaces than termsock / UNIX socket.
 * Support json-rpc

License information
-------------------

Copyright (c) 2010-2012 Ben Bass <benbass@codedstructure.net>
All rights reserved.

See the file "LICENSE" for information terms & conditions
for usage, and a DISCLAIMER OF ALL WARRANTIES.
