import lxml
import urllib
import random
import subprocess, threading, Queue
import numpy as np

def pls_urls():
    with open('urls.txt', 'r') as f:
        return [r.strip() for r in f]

def stream_urls_from_pls(pls_data):
    return [row.split('=')[1].strip() for row in pls_data if row.startswith('File')]

def stream_urls():
    for pls in pls_urls():
        yield stream_urls_from_pls(urllib.urlopen(pls))

def single_stream_urls():
    return map(random.choice, stream_urls())

def numpy_stream(stream_url, n_samples=44000):
    proc = subprocess.Popen(['ffmpeg', '-i', stream_url, '-f', 's16le', '-acodec', 'pcm_s16le', 'pipe:1'], stdout=subprocess.PIPE)
    outq = Queue.Queue(maxsize=10)
    def reader_worker():
        try:
            while not proc.returncode:
                outq.put(np.fromfile(proc.stdout, np.int16, n_samples, ''))
        finally:
            outq.put('done')
    thread = threading.Thread(target=reader_worker)
    thread.start()
    while 1:
        row = outq.get()
        if row == 'done':
            break
        yield row

def numpy_all_streams(n_samples=44000):
    stream_urls = single_stream_urls()
    gens = [iter(numpy_stream(url, n_samples)) for url in stream_urls]
    while gens:
        row = []
        for gen in gens:
            try:
                row.append(next(gen))
            except StopIteration:
                gens.remove(gen)
        yield row
