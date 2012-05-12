
import socket
import sys
import select
import time
import os


# equivalent of 'socat - UNIX:/path/to/socket'
class TermSock(object):
    # docs for python 2.7 select reference select.PIPE_BUF,
    # which is at least 512 bytes (POSIX) and is the minimum
    # amount of bytes writable to a fd returned from select
    # as in the writable state.
    PIPE_BUF = 512

    STDIN_FD = sys.stdin.fileno()    # normally 0
    STDOUT_FD = sys.stdout.fileno()  # normally 1

    def __init__(self, sock_name):
        self.sock_name = sock_name
        self.stdin_log = []
        self.stdout_log = []
        self.sock_log = []
        self._out_fds = set()

    def _connect(self):
        # must hold on to socket object so it doesn't get GC'd
        # and closed, even though the only thing we care about
        # is its fileno()
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        while True:
            try:
                self.s.connect(self.sock_name)
            except socket.error:
                time.sleep(0.1)
            else:
                break

        self.s_fd = self.s.fileno()

    def _poll(self):
        """
        @return: whether we are finished.
        """
        r, w, e = select.select([TermSock.STDIN_FD,
                                 self.s_fd],
                                list(self._out_fds),
                                [])

        if e:
            return True
        if TermSock.STDIN_FD in r:
            stdin_input = os.read(TermSock.STDIN_FD,
                                  TermSock.PIPE_BUF).decode()
            if not stdin_input:
                return True
            self.stdin_log.append(stdin_input)
            self._out_fds.add(self.s_fd)
        if self.s_fd in r:
            sock_input = os.read(self.s_fd, TermSock.PIPE_BUF).decode()
            if not sock_input:
                return True
            self.sock_log.append(sock_input)
            self._out_fds.add(TermSock.STDOUT_FD)
        if TermSock.STDOUT_FD in w and self.sock_log:
            self.sock_log = ''.join(self.sock_log)
            wlen = os.write(TermSock.STDOUT_FD,
                            ''.join(self.sock_log).encode())
            remainder = self.sock_log[wlen:]
            if remainder:
                self.sock_log = [remainder]
            else:
                self.sock_log = []
                self._out_fds.remove(TermSock.STDOUT_FD)
        if self.s_fd in w and self.stdin_log:
            self.stdin_log = ''.join(self.stdin_log)
            wlen = os.write(self.s_fd, ''.join(self.stdin_log).encode())
            remainder = self.stdin_log[wlen:]
            if remainder:
                self.stdin_log = [remainder]
            else:
                self.stdin_log = []
                self._out_fds.remove(self.s_fd)

    def mainloop(self):
        self._connect()
        while not self._poll():
            pass


def terminal(addr):
    ts = TermSock(addr)
    ts.mainloop()


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    if args:
        terminal(args[0])
    else:
        print("Usage: %s [debug socket address]" % sys.argv[0])

if __name__ == '__main__':
    main()
