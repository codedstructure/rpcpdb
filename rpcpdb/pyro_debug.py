#!/usr/bin/python -u

import termsock
import Pyro.core


s = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/rpc")
dbg_path = s.debug_func('next_prime')

termsock.TermSock(dbg_path).mainloop()
