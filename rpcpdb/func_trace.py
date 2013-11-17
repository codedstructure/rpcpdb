"""
Tracing of functions, writing trace files.

Copyright 2013 Ben Bass <ben.bass@codedstructure.net>
Licence: MIT - http://www.opensource.org/licenses/mit-license.php
"""


import sys
import inspect


class Tracer(object):
    def __init__(self, tracepath=None):
        if tracepath is None:
            self.tracefile = sys.stdout
        else:
            self.tracefile = open(tracepath, 'w')

    def __call__(self, frame, event, arg):
        if event in ('call', 'return'):
            return LocalTracer(frame, event, tracefile=self.tracefile)


class LocalTracer(object):

    def __init__(self, frame, event, tracefile=None):
        if tracefile is None:
            tracefile = sys.stdout
        self.tracefile = tracefile
        self.fname = inspect.getframeinfo(frame).function

        if event == 'call':
            self.tracefile.write("=> {}\n".format(self.fname))

        self.obj_source, self.line_offset = inspect.getsourcelines(frame.f_code)
        self.max_line_len = min(80, len(max(self.obj_source, key=len)))
        self.fmt_str = "{}:{} ||| {:%d} ||| {}\n" % self.max_line_len

    def __call__(self, frame, event, arg):
        if event == 'line':
            fname = frame.f_code.co_filename
            lineno = frame.f_lineno
            sourceline = self.obj_source[lineno - self.line_offset].rstrip()
            localvars = frame.f_locals.copy()
            # design decision - omit self here. There are occasions it will be
            # useful & more cases where other things are just clutter, but...
            localvars.pop('self', None)

            self.tracefile.write(self.fmt_str.format(fname, lineno,
                                                     sourceline, localvars))
            return self
        elif event == 'return':
            self.tracefile.write("<= ({})  # from: {}\n".format(arg,
                                                                self.fname))

#
# The following may be helpful if using this module standalone as an example.
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


def main():
    old_trace = sys.gettrace()
    sys.settrace(Tracer())
    try:
        fact(testfunc())
    finally:
        sys.settrace(old_trace)


if __name__ == '__main__':
    main()
