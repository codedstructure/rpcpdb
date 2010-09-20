#!/usr/bin/python -u

# be compatible with Python 2.5
from __future__ import with_statement

import tempfile

from updb import UPdb

class UPdb_mixin(object):
    _updb_debug_func = {}

    def debug_func(self, f, once=True, force=True):
        if f not in self._updb_debug_func:
            func = getattr(self, f)
            self._updb_debug_func[f] = func
            pdb_sock_path = "%s/pdb_sock"%tempfile.mkdtemp(prefix='updb_')
            def _(*o, **k):
                if once:
                    self.undebug_func(f)
                with UPdb(pdb_sock_path, level=1, force=force):
                    return func(*o, **k)
            setattr(self, f, _)
            return pdb_sock_path

    def undebug_func(self, f):
        if f in self._updb_debug_func:
            setattr(self, f, self._updb_debug_func.pop(f))


def main(options):
    if options.funcname:
        # get a client connection
        c = None # TODO: do this in a generic way
        sock_name = c.debug_func(options.funcname, options.once, force=options.force)
    else:
        sock_name = options.sockname

    from termsock import TermSock
    dbg = TermSock(sock_name)
    dbg.mainloop()

if __name__ == '__main__':
    import optparse
    usage = "updb: connect to a UPdb debugger"
    parser = optparse.OptionParser(usage=usage)
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
