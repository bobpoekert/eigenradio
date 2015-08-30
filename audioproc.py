import numpy.fft as fft
import numpy as np

def entropy(chunk):
    chunk = chunk.astype(np.int32)
    chunk += 2**15
    counts = np.bincount(chunk)
    probs = counts.astype(np.float64) / len(counts)
    return -np.sum(probs)**2

def merge_streams(sample_streams):
    for chunk in sample_streams:
        chunk = map(np.copy, chunk) # defensive copy
        freqs = [fft.fft(p) for p in chunk if len(p) > 0]
        entropies = [entropy(p) for p in chunk if len(p) > 0]
        total_entropy = sum(entropies)
        print total_entropy
        res = None
        for buf, e in zip(freqs, entropies):
            frac = e / total_entropy
            if res is None:
                res = buf * frac
            else:
                res += buf * frac
        yield fft.ifft(res / len(chunk)).astype(np.int16)

if __name__ == '__main__':
    import shoutcast, subprocess, ffmpeg
    urls = list(shoutcast.n_stream_urls(10))
    print urls
    streams = shoutcast.numpy_streams(urls, sample_duration=0.25)
    #with open('test.pcm', 'w') as writer:
    #    for row in merge_streams(streams):
    #        writer.write(row)
    with ffmpeg.audio_writer('test.aac') as writer:
        ffmpeg.copy_to(merge_streams(streams), writer)
