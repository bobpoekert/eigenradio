import subprocess
import tornado.iostream
import numpy as np

audio_rate = 44100
channels = 1

raw_audio_options = [
    '-f', 's16le',
    '-acodec', 'pcm_s16le',
    '-ar', str(audio_rate),
    '-ac', str(channels)
]

def audio_reader(infname):
    return subprocess.Popen(['ffmpeg', '-i', infname] + raw_adudio_options + ['pipe:1'],
        stdout=subprocess.PIPE)

def numpy_reader(infname, sample_duration=1):
    print infname
    proc = audio_reader(infname)
    n_samples = sample_duration * audio_rate
    while not proc.returncode:
        yield np.fromfile(proc.stdout, np.int16, n_samples, '')

def audio_writer(outf, format='aac', bitrate='128k', onclose=None):
    proc = subprocess.Popen(
        ['ffmpeg', '-i', 'pipe:0'] + raw_audio_options + [
        '-acodec', 'aac',
        '-ac', str(channels),
        '-ar', str(audio_rate),
        '-ab', bitrate,
        outf if type(outf) == str else 'pipe:1'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)


    if type(outf) != str:
        if onclose is None:
            onclose = outf.close
        instream = iostream.PipeIOStream(proc.stdout.fileno())
        instream.read_until_close(onclose, streaming_callback=outf.write)

    return proc.stdin
