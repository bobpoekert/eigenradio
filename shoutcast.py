import lxml
import urllib
import random
import subprocess, threading, Queue
import ffmpeg
import numpy as np

def pls_urls():
    with open('urls.txt', 'r') as f:
        return [r.strip() for r in f]

def stream_urls_from_pls(pls_data):
    return [row.split('=')[1].strip() for row in pls_data if row.startswith('File')]

def stream_urls():
    for pls in pls_urls():
        yield stream_urls_from_pls(urllib.urlopen(pls))

def n_stream_urls(n):
    for pls in random.sample(pls_urls(), n):
        yield stream_urls_from_pls(urllib.urlopen(pls))

def numpy_stream(stream_urls, sample_duration=1):
    for stream_url in stream_urls:
        for chunk in ffmpeg.numpy_reader(stream_url, sample_duration):
            yield chunk

def numpy_streams(urls, sample_duration=1):
    gens = [iter(numpy_stream(url, sample_duration)) for url in urls]
    while gens:
        row = []
        for gen in gens:
            try:
                v = next(gen)
                if v is not None:
                    row.append(v)
            except StopIteration:
                gens.remove(gen)
        if row:
            yield row
