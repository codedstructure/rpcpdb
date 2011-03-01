#!/usr/bin/python -u

# be compatible with Python 2.5
from __future__ import with_statement

import pdb, socket, sys, os, tempfile

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


class UPdb_mixin(object):
    """
    This is designed to be mixed-in to an RPC server
    object. It allows an RPC client to register a
    RPC method as being debuggable.

    On triggering, subsequent calls to that method
    will trigger a pdb breakpoint (currently with
    interaction over a unix socket)
    """
    # this is a map from function name to
    # (function, unix_socket_path) pairs.
    _updb_debug_func = {}

    def debug_func(self, f, once=True, force=True):
        """
        @param f: function name
        @param once: one-shot debug - undebug after first hit
        @param force: override any existing unix socket
        @return: path to debug socket
        """
        if f in self._updb_debug_func:
            return self._updb_debug_func[f][1]
        else:
            func = getattr(self, f)
            pdb_sock_path = "%s/pdb_sock"%tempfile.mkdtemp(prefix='updb_')
            self._updb_debug_func[f] = (func, pdb_sock_path)
            def _(*o, **k):
                if once:
                    self.undebug_func(f)
                with UPdb(pdb_sock_path, level=1, force=force):
                    return func(*o, **k)
            setattr(self, f, _)
            return pdb_sock_path

    def undebug_func(self, f):
        """
        don't debug this function anymore.
        """
        if f in self._updb_debug_func:
            setattr(self, f, self._updb_debug_func.pop(f)[0])
