
import socket, sys, select, time, os

# equivalent of 'socat - UNIX:/path/to/socket'
class TermSock(object):
    # docs for python 2.7 select reference select.PIPE_BUF,
    # which is at least 512 bytes (POSIX) and is the minimum
    # amount of bytes writable to a fd returned from select
    # as in the writable state.
    PIPE_BUF = 512

    STDIN_FD = sys.stdin.fileno()    # normally 0
    STDOUT_FD = sys.stdout.fileno()  # normally 1
    STDERR_FD = sys.stderr.fileno()  # normally 2

    def __init__(self, sock_name):
        self.sock_name = sock_name
        self.stdin_log = []
        self.stdout_log = []
        self.sock_log = []

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
        r,w,e = select.select([TermSock.STDIN_FD,
                               self.s_fd],
                              [TermSock.STDOUT_FD,
                               TermSock.STDERR_FD,
                               self.s_fd],
                              [])
        if e:
            return True
        if TermSock.STDIN_FD in r:
            stdin_input = os.read(TermSock.STDIN_FD, TermSock.PIPE_BUF)
            if not stdin_input:
                return True
            self.stdin_log.append(stdin_input)
        if self.s_fd in r:
            sock_input = os.read(self.s_fd, TermSock.PIPE_BUF)
            if not sock_input:
                return True
            self.sock_log.append(sock_input)
        if TermSock.STDOUT_FD in w and self.sock_log:
            self.sock_log = ''.join(self.sock_log)
            wlen = os.write(TermSock.STDOUT_FD, ''.join(self.sock_log))
            remainder = self.sock_log[wlen:]
            self.sock_log = [remainder] if remainder else []
        if self.s_fd in w and self.stdin_log:
            self.stdin_log = ''.join(self.stdin_log)
            wlen = os.write(self.s_fd, ''.join(self.stdin_log))
            remainder = self.stdin_log[wlen:]
            self.stdin_log = [remainder] if remainder else []

    def mainloop(self):
        self._connect()
        while not self._poll():
            pass
