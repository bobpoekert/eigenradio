from tornado import netutil, ioloop, iostream, httpclient, stack_context
import os, threading, subprocess, Queue, fcntl, ctypes
import shoutcast, audioproc, socket_error

libc = ctypes.cdll.LoadLibrary('libc.so.6')
splice_syscall = libc.splice

SPLICE_F_NONBLOCK = 0x02
SPLICE_F_MOVE = 0x01

try:
    chunk_size = os.pathconf('.', os.pathconf_names['PC_PIPE_BUF'])
except:
    print 'pathconf failed'
    import resource
    chunk_size = resource.getpagesize()

def splice(left, right):
    total = 0

    while 1:
        code = splice_syscall(left, 0, right, 0, chunk_size, SPLICE_F_NONBLOCK | SPLICE_F_MOVE)

        if code == -1:
            errno = get_errno()
            socket_error.raise_socket_error(errno)

        total += code

        if code < chunk_size:
            break

    return total

class shunt(object):

    def __init__(self, inf, outf, ioloop=None):
        self.inf = inf
        self.outf = outf
        if ioloop is None:
            self.ioloop = IOLoop.getInstance()
        else:
            self.ioloop = ioloop
        self.instream = iostream.IOStream(inf)
        self.outstream = iostream.IOStream(outf)


http_response = '\r\n'.join([
    'HTTP/1.1 200 OK',
    'Server: :p',
    'Connection: close',
    'Content-Type: audio/x-aac',
    'Transfer-Encoding: chunked',
    ''])

pipe_read, pipe_write = os.pipe()

def encode():
    proc = subprocess.Popen([
        'ffmpeg', '-i', 'pipe:0', '-f', 's16le', '-acodec', 'faac', 'pipe:1'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return (proc.stdin, proc.stdout)

def processing_worker(outf):
    for chunk in audioproc.merge_streams(shoutcast.numpy_all_streams()):
        chunk.tofile(outf)

def process():
    encode_in, encode_out = encode()
    processing_thread = threading.Thread(target=processing_worker, args=(encode_in,))
    processing_thread.start()
