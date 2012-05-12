#!/usr/bin/python -u

import termsock
import Pyro.core


s = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/rpc")
dbg_path = s.debug_func('next_prime', match_criteria={'p':79})
dbg_path = s.debug_func('next_prime', ignore_count=2)

termsock.terminal(dbg_path)
