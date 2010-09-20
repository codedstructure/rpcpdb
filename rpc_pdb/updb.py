#!/usr/bin/python -u

# be compatible with Python 2.5
from __future__ import with_statement

import pdb, socket, sys, os

class UPdb(pdb.Pdb):
    def __init__(self, sock_path, level=0, force=False):
        if force:
            try:
                os.remove(sock_path)
            except:
                pass
        self._sock_path = sock_path
        self._level = level
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(self._sock_path)
        self._sock.listen(1)
        self._conn = self._sock.accept()[0]
        self._handle = self._conn.makefile('rw')
        self._old_stdin = sys.stdin
        self._old_stdout = sys.stdout
        pdb.Pdb.__init__(self,
                         stdin=self._handle,
                         stdout=self._handle)
        sys.stdout = sys.stdin = self._handle

    def __enter__(self):
        target_frame = sys._getframe().f_back
        for count in range(self._level):
            try:
            	target_frame = target_frame.f_back
            except AttributeError:
                break
        self.set_trace(target_frame)

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdin = self._old_stdin
        sys.stdout = self._old_stdout

        self._conn.shutdown(socket.SHUT_RDWR)
        os.remove(self._sock_path)
        os.rmdir(os.path.dirname(self._sock_path))
