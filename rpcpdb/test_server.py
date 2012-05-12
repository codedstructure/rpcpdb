#!/usr/bin/python

# This is a simple non-RPC test case which runs a loop
# in a background thread and then inserts a debug hook

import threading
import time
from rpcpdb import terminal, UPdb_mixin


class PrimeServer(UPdb_mixin):
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

    def test_func(self, **k):
        if k.pop('thing', None) == 'hello':
            print("Hiya")
        else:
            print("OK then.")

    def mainloop(self):
        p = 0
        while p < 150:
            p = self.next_prime(p)
            print(p)
            time.sleep(0.1)


def main():
    ps = PrimeServer()
    # test basic parameter criteria match
    t = threading.Thread(target=ps.mainloop)
    t.daemon = True
    t.start()
    time.sleep(2)
    terminal(ps.debug_func('next_prime',
                           match_criteria={'p': 97}))
    terminal(ps.debug_func('next_prime',
                           ignore_count=5))
    t.join()

    # test keyword criteria match
    def _():
        time.sleep(2)
        ps.test_func()
        time.sleep(2)
        ps.test_func(thing='hello')
    t = threading.Thread(target=_)
    t.daemon = True
    t.start()
    terminal(ps.debug_func('test_func',
                           match_criteria={'thing': 'hello'}))
    terminal(ps.debug_func('test_func',
                           match_criteria={'thing': 'hello'}))
    time.sleep(1)
    t.join()

if __name__ == '__main__':
    main()
