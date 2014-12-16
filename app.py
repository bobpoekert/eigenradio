from tornado import netutil, ioloop, iostream, httpclient, stack_context
import os, threading, subprocess, Queue
import shoutcast, audioproc

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

def copy_chunked_encoding_to_pipe(inf, outf):
    

def process():
    encode_in, encode_out = encode()
    processing_thread = threading.Thread(target=processing_worker, args=(encode_in,))
    processing_thread.start()
