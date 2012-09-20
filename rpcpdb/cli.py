#!/usr/bin/python -u

import ast
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
            param, value = map(''.strip, match.split(':', 1))
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
        sock_name = c.debug_func(options.funcname,
                                 options.once,
                                 force=options.force,
                                 match_criteria=match_criteria,
                                 ignore_count=options.ignore_count)
    elif options.console:
        c = get_api_connection()
        sock_name = c.debug_interactive_console()
    else:
        sock_name = options.sockname

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
    options, args = parser.parse_args()
    if len(filter(None, (options.sockname,
                         options.funcname,
                         options.console))) != 1:
        parser.error("Specify exactly one of --funcname, --sockname or --console")
    if options.match and not options.funcname:
        parser.error("--match can only be specified for --funcname")

    debug(options)


if __name__ == '__main__':
    main()
