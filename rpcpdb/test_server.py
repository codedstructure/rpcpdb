#!/usr/bin/python -u

# This is a simple non-RPC test case which runs a loop
# in a background thread and then inserts a debug hook

import threading
import time
from rpcpdb.termsock import terminal
import updb

class PrimeServer(updb.UPdb_mixin):
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

    def mainloop(self):
        p = 0
        while p < 200:
            p = self.next_prime(p)
            print(p)
            time.sleep(0.1)

def main():
    ps = PrimeServer()
    t = threading.Thread(target = ps.mainloop)
    t.daemon=True
    t.start()
    time.sleep(2)
    terminal(ps.debug_func('next_prime',
                           match_criteria={'p':97}))
    t.join()

if __name__ == '__main__':
    main()