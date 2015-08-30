import subprocess
import tornado.iostream
import numpy as np
import struct, sys

audio_rate = 44100
channels = 1

raw_audio_options = [
    '-f', 's16le',
    '-acodec', 'pcm_s16le',
    '-ar', str(audio_rate),
    '-ac', str(channels)
]

def audio_reader(infname):
    return subprocess.Popen(['ffmpeg', '-i', infname] + raw_audio_options + ['pipe:1'],
        stderr=open('/dev/null', 'w'),
        stdout=subprocess.PIPE)

def numpy_reader(infname, sample_duration=1):
    print infname
    proc = audio_reader(infname)
    n_samples = int(sample_duration * audio_rate)
    while not proc.returncode:
        buf = np.empty((n_samples,), dtype=np.int16)
        data = proc.stdout.read(n_samples*2)
        buf.data[:len(data)] = data
        yield buf

def is_string(v):
    return type(v) in (str, unicode)

def audio_writer(outf, format='aac', bitrate='128k', onclose=None):
    proc = subprocess.Popen(
        ['ffmpeg', '-y',
         '-f', 's16le',
         '-acodec', 'pcm_s16le',
         '-r', str(audio_rate),
         '-ac', str(channels),
         '-i', '-',
         '-acodec', 'libmp3lame',
         '-f', 'mp3',
         '-b', '128k',
        outf if is_string(outf) else 'pipe:1'],
        stdin=subprocess.PIPE,
        #stderr=open('/dev/null', 'w'),
        stdout=subprocess.PIPE)

    #if not is_string(outf):
    #    if onclose is None:
    #        onclose = outf.close
    #    instream = iostream.PipeIOStream(proc.stdout.fileno())
    #    instream.read_until_close(onclose, streaming_callback=outf.write)

    return (proc.stdin, proc.stdout)

def copy_to(inseq, outf):
    for row in inseq:
        if row.dtype.byteorder == '>' or (row.dtype.byteorder == '=' and sys.byteorder == 'big'):
            row = row.byteswap()
        outf.write(row.ravel().view('b').data)

