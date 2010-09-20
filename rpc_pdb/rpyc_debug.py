#!/usr/bin/python -u

# be compatible with Python 2.5
from __future__ import with_statement

import termsock, rpyc

def main(options):
    if options.funcname:
        c = rpyc.connect('localhost', 18861)
        s = c.root
        sock_name = s.debug_func(options.funcname, options.once, force=options.force)
    else:
        sock_name = options.sockname
    print sock_name

    dbg = termsock.TermSock(sock_name)
    dbg.mainloop()

if __name__ == '__main__':
    import optparse
    usage = "updb: connect to a UPdb debugger"
    parser = optparse.OptionParser(usage=usage)
    # TODO: consider a force option which removes any existing
    # unix socket
    parser.add_option("-s", "--sockname", dest="sockname", help="UNIX-domain socket path")
    parser.add_option("-a", "--funcname", dest="funcname", help="API function to debug")
    parser.add_option("-o", "--once", dest="once", action="store_false", help="Set breakpoint as once-only (default)", default=True)
    parser.add_option("-f", "--force", dest="force", action="store_true", help="Force (overwrite any previous socket)")
    options,args = parser.parse_args()
    if options.sockname and options.funcname:
        parser.error("Options --sockname and --funcname are mutually exlucsive")
    if not(options.sockname or options.funcname):
        parser.error("Must specify either --sockname or --funcname")

    main(options)
