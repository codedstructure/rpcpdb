import time
import Pyro.core

s = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/rpc")

p = 0
while True:
    time.sleep(0.5)
    p = s.next_prime(p)
    print(p)
