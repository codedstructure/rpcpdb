#!/usr/bin/python -u

# be compatible with Python 2.5
from __future__ import with_statement
import inspect

import pdb
import socket
import sys
import os
import tempfile


class UPdb(pdb.Pdb):
    def __init__(self, sock_path, level=0, force=False):
        if force:
            try:
                os.remove(sock_path)
            except OSError:
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

    def debug_func(self, f, once=True, force=True,
                   match_criteria=None, ignore_count=0):
        """
        @param f: function name
        @param once: one-shot debug - undebug after first hit
        @param force: override any existing unix socket
        @param match_criteria: dictionary of param name/value matches
        @param ignore_count: don't trigger for ignore_count matches
        @return: path to debug socket
        """
        if f in self._updb_debug_func:
            return self._updb_debug_func[f][1]
        else:
            func = getattr(self, f)
            pdb_sock_path = "%s/pdb_sock" % tempfile.mkdtemp(prefix='updb_')
            self._updb_debug_func[f] = (func, pdb_sock_path)

            def arg_match(o, k):
                """
                TODO: currently this will require an exact match on
                any varargs/keyword args list of the target function. FIX
                """
                if not match_criteria:
                    # we always match if we have no match criteria
                    return True
                # getcallargs is only 2.7+
                # see also ActiveState recipe 551779 or inspect.py code.
                called_with = inspect.getcallargs(func, *o, **k)
                for key, val in match_criteria.items():
                    if key in called_with and called_with[key] == val:
                        return True
                return False

            def debug_check(*o, **k):
                if arg_match(o, k):
                    debug_check._ignore_count -= 1
                    if debug_check._ignore_count <= 0:
                        if once:
                            self.undebug_func(f)
                        with UPdb(pdb_sock_path, level=1, force=force):
                            return func(*o, **k)
                # we're not debugging you, this time...
                return func(*o, **k)
            # use a function attribute to store the skip count;
            # decrement this on each matched call. Trigger at <= 0
            debug_check._ignore_count = ignore_count

            setattr(self, f, debug_check)
            return pdb_sock_path

    def undebug_func(self, f):
        """
        don't debug this function anymore.
        """
        if f in self._updb_debug_func:
            setattr(self, f, self._updb_debug_func.pop(f)[0])
