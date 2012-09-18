rpcpdb
======

Copyright (c) 2010-2012 Ben Bass <benbass@codedstructure.net>

All rights reserved.

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

Done
----
 * v0.2 - Add trigger criteria which check incoming arguments so the
   user can ensure the right client triggers the breakpoint

License information
-------------------

See the file "LICENSE" for information terms & conditions
for usage, and a DISCLAIMER OF ALL WARRANTIES.


Changes
-------
0.3.2
 * add debug_interactive_console mixin function to gain an interactive
   console into the target RPC API
0.3.1
 * add .hgignore file
 * add updb creation without specifying a socket name. One will be
   created 'at random' and the name available through the debug_socket
   read-only property.
0.3
 * Added ignore_count functionality for skipping a matched breakpoint
   n times
0.2.1
 * No functional changes; updates to Trove classifiers only
0.2
 * Python 3 support (3.2+ only)
 * parameter matching to trigger debugger (conditional debugging)
0.1.1
 * fix issue where select call in termsock was continually
   finding writable FDs, causing 100% CPU usage
0.1
 * first alpha release.
