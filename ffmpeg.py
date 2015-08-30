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

def hexstring_to_bytes(hex_string):
    res = ""
    for i in range(0, len(hex_string), 2):
            res += chr(int(hex_string[i:i+2], 16))

    return res

def write_wav_header(out_file, fmt, codec_private_data, data_len):

    extradata = hexstring_to_bytes(codec_private_data)

    fmt['cbSize'] = len(extradata)
    fmt_len = 18 + fmt['cbSize']
    wave_len = len("WAVEfmt ") + 4 + fmt_len + len('data') + 4

    out_file.write("RIFF")
    out_file.write(struct.pack('<L', wave_len))
    out_file.write("WAVEfmt ")
    out_file.write(struct.pack('<L', fmt_len))
    out_file.write(struct.pack('<H', fmt['wFormatTag']))
    out_file.write(struct.pack('<H', fmt['nChannels']))
    out_file.write(struct.pack('<L', fmt['nSamplesPerSec']))
    out_file.write(struct.pack('<L', fmt['nAvgBytesPerSec']))
    out_file.write(struct.pack('<H', fmt['nBlockAlign']))
    out_file.write(struct.pack('<H', fmt['wBitsPerSample']))
    out_file.write(struct.pack('<H', fmt['cbSize']))
    out_file.write(extradata)
    out_file.write("data")
    out_file.write(struct.pack('<L', data_len))

def write_default_wav_header(outf):
    write_wav_header(
            outf,
            {
                'wFormatTag':0x161,
                'nChannels':channels,
                'nSamplesPerSec':audio_rate,
                'nAvgBytesPerSec':audio_rate*2,
                'wBitsPerSample':16,
                'nBlockAlign':8192,
                'cbSize':0
            },
            "008800000f0000000000",
            2**31)


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
        outf if is_string(outf) else 'pipe:1'],
        stdin=subprocess.PIPE,
        #stderr=open('/dev/null', 'w'),
        stdout=subprocess.PIPE)

    #if not is_string(outf):
    #    if onclose is None:
    #        onclose = outf.close
    #    instream = iostream.PipeIOStream(proc.stdout.fileno())
    #    instream.read_until_close(onclose, streaming_callback=outf.write)

    return proc.stdin

def copy_to(inseq, outf):
    for row in inseq:
        if row.dtype.byteorder == '>' or (row.dtype.byteorder == '=' and sys.byteorder == 'big'):
            row = row.byteswap()
        outf.write(row.ravel().view('b').data)

