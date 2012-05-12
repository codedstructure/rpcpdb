#!/usr/bin/env python -u

import xmlrpclib
import termsock

s = xmlrpclib.ServerProxy('http://localhost:8000')
dbg_path = s.debug_func('next_prime')

termsock.terminal(dbg_path)
