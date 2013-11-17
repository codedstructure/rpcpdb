#!/usr/bin/python -u

"""
Command line interface to rpcpdb. This becomes an RPC client allowing
RPC methods to be debugged & traced.

Copyright 2010-2013 Ben Bass <benbass@codedstructure.net>
Licence: MIT - http://www.opensource.org/licenses/mit-license.php
"""

import os
import ast
import signal

from rpcpdb import termsock


def get_api_connection():
    """
    replace this with something to return a proxy to your API
    """
    raise NotImplementedError('this function should be replaced')


def debug(options):
    if options.funcname:
        # get a client connection
        c = get_api_connection()
        match_criteria = {}
        for match in (options.match or []):
            param, value = [x.strip() for x in match.split(':', 1)]
            if not param and not value:
                raise ValueError('invalid match definition "%s"' % match)
            try:
                real_value = ast.literal_eval(value)
            except SyntaxError:
                raise ValueError('invalid match definition "%s"' % match)
            except ValueError:
                # literal_eval gives a ValueError where I would expect
                # a NameError...
                real_value = value
            match_criteria[param] = real_value
        if options.trace:
            c.trace_func(options.funcname,
                         options.trace_logfile,
                         once=options.once,
                         match_criteria=match_criteria,
                         ignore_count=options.ignore_count)
            sock_name = None
        else:
            sock_name = c.debug_func(options.funcname,
                                     once=options.once,
                                     force=options.force,
                                     match_criteria=match_criteria,
                                     ignore_count=options.ignore_count)

        def _cleanup(*args):
            # This undoes the breakpoint in the event we are
            # rudely interrupted.
            c.undebug_func(options.funcname)
            raise SystemExit('Aborted.')

        signal.signal(signal.SIGINT, _cleanup)
        signal.signal(signal.SIGTERM, _cleanup)

    elif options.console:
        c = get_api_connection()
        sock_name = c.debug_interactive_console()
    else:
        sock_name = options.sockname

    if sock_name is not None:
        dbg = termsock.TermSock(sock_name)
        dbg.mainloop()


def main():
    import optparse
    usage = "%prog: connect to a UPdb debugger"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-s", "--sockname",
                      dest="sockname",
                      help="UNIX-domain socket path")
    parser.add_option("-a", "--funcname",
                      dest="funcname",
                      help="API function to debug")
    parser.add_option("-c", "--console",
                      dest="console",
                      action="store_true",
                      help="Interactive console")
    parser.add_option("-m", "--match",
                      dest="match",
                      action="append",
                      help="Add a match criteria in form 'param:value'")
    parser.add_option("-o", "--once",
                      dest="once",
                      action="store_false",
                      help="Set breakpoint as once-only (default)",
                      default=True)
    parser.add_option("-i", "--ignore_count",
                      dest="ignore_count",
                      default=0,
                      type=int,
                      help="Ignore count (default 0)")
    parser.add_option("-f", "--force",
                      dest="force",
                      action="store_true",
                      help="Force (overwrite any previous socket)")
    parser.add_option("-t", "--trace",
                      dest="trace",
                      action="store_true",
                      help="Trace (rather than debug) function call")
    parser.add_option("-l", "--trace-logfile",
                      dest="trace_logfile",
                      default=os.path.abspath("trace.out"),
                      help="Path to trace file to store")
    options, args = parser.parse_args()
    if len(filter(None, (options.sockname,
                         options.funcname,
                         options.console))) != 1:
        parser.error("Specify exactly one of --funcname, --sockname or --console")
    if (any((options.match, options.ignore_count, options.trace)) and
        not options.funcname):
        parser.error("options requiring --funcname given")
    if options.trace_logfile and not options.trace:
        parser.error("--trace-logfile can only be specified with --trace")
    if options.force and options.trace:
        parser.error("--force can not be specified with --trace")

    debug(options)


if __name__ == '__main__':
    main()
