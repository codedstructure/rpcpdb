#!/usr/bin/env python -u

import xmlrpclib
import time

s = xmlrpclib.ServerProxy('http://localhost:8000')
# Print list of available methods
print(s.system.listMethods())

p = 0
while True:
    time.sleep(0.5)
    p = s.next_prime(p)
    print(p)
