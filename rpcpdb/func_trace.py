"""
Tracing of functions, writing trace files.

Copyright 2013 Ben Bass <benbass@codedstructure.net>
Licence: MIT - http://www.opensource.org/licenses/mit-license.php
"""


import os
import sys
import inspect


class Tracer(object):
    """
    set this with sys.settrace() to perform tracing
    """
    def __init__(self, tracepath=None):
        """
        @param tracepath: file object to write trace log to
        """
        if tracepath is None:
            self.tracefile = sys.stdout
        else:
            self.tracefile = open(tracepath, 'w')

    def __call__(self, frame, event, arg):
        """
        top-level trace function

        see sys.settrace() documentation
        """
        if event in ('call',):
            return LocalTracer(frame, event, tracefile=self.tracefile)
        else:
            self.tracefile.write('>> %s ' % event)


class LocalTracer(object):
    """
    local trace class - this is instantiated by the global Tracer() class
    """

    def __init__(self, frame, event, tracefile=None):
        """
        @param frame, event - passed in from top-level tracer
        @param tracefile: file object to write trace log to
        """
        if tracefile is None:
            tracefile = sys.stdout
        self.tracefile = tracefile
        self.fname = inspect.getframeinfo(frame).function

        self.obj_source = None
        self.line_offset = None
        self._skipping = False
        try:
            self.obj_source, self.line_offset = inspect.getsourcelines(frame.f_code)
        except IOError:
            # source code unavailable
            pass
        else:
            self.max_line_len = min(80, len(max(self.obj_source, key=len)))
            self.fmt_str = "{}:{:<4} ||| {:%d} ||| {{{}}}\n" % self.max_line_len
            filename = frame.f_code.co_filename
            # only keep last two elements of filename path
            self.srcfile = os.path.sep.join(filename.split(os.path.sep)[-2:])

        if event == 'call':
            self.tracefile.write("=> {}\n".format(self.fname))

    def _shortstr(self, s):
        if len(repr(s)) > 80:
            return repr(s)[:80] + '...'
        else:
            return repr(s)

    def __call__(self, frame, event, arg):
        """
        local trace function, called on each line/call/return/exception etc
        within a local scope

        See sys.settrace() documentation
        """
        if event == 'line':
            if self.obj_source is None:
                if not self._skipping:
                    self.tracefile.write("--\n")
                    self._skipping = True
                return None

            lineno = frame.f_lineno
            try:
                sourceline = self.obj_source[lineno - self.line_offset].rstrip()
            except Exception:
                # perhaps something is out of sync or source doesn't exist
                if not self._skipping:
                    self.tracefile.write("---\n")
                    self._skipping = True
                return None
            else:
                self._skipping = False
                localvars = frame.f_locals.copy()
                # design decision - omit certain things here. There are
                # occasions when they will be useful & more cases where other
                # things are just clutter, but...
                names_to_omit = ['self', 'builtins']
                names_to_omit.extend([key for key in localvars if key.startswith('__')])
                for key in names_to_omit:
                    localvars.pop(key, None)
                for key, value in list(localvars.items()):
                    localvars[key] = self._shortstr(value)
                context = ', '.join(('{}: {}'.format(k, v) for k, v in localvars.items()))

                self.tracefile.write(self.fmt_str.format(self.srcfile, lineno,
                                                         sourceline, context))
            return self

        elif event == 'return':
            self.tracefile.write("<= ({})  # from: {}\n".format(self._shortstr(arg),
                                                                self.fname))

        elif event == 'exception':
            # support for exceptions
            self.tracefile.write('%s(%r)\n' % (arg[0].__name__, arg[1]))

        else:
            # This "shouldn't" happen...
            self.tracefile.write('>>> %s, %s\n' % (event, arg))

#
# The following may be helpful if using this module standalone as an example.
#
# Note this takes a long time on Python3, due to module initialisation in python
# Might want to turn off tracing of global-level module evaluation in future...
#


def testfunc():
    i = 0
    while i < 10:
        i = i * 2 + 1
        print (i)
    return i


def fact(i):
    if i == 0:
        return 1
    else:
        return i * fact(i - 1)


def reciprocal(i):
    return 1.0 / i


def test_exc():
    try:
        for i in range(3, -1, -1):
            z = reciprocal(i)
            print(z)
    except ZeroDivisionError:
        print("Done")


def test_c():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    print(s.getpeername())


def main():
    old_trace = sys.gettrace()
    sys.settrace(Tracer())
    try:
        fact(testfunc())
        test_exc()
        test_c()
    finally:
        sys.settrace(old_trace)


if __name__ == '__main__':
    main()
