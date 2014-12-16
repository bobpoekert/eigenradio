import shoutcast
import numpy.fft as fft
import numpy as np

def merge_streams(sample_streams):
    for chunk in sample_streams:
        freqs = [fft.fft(p) for p in chunk]

        # compute P(this stream | this sample) for all samples
        # normalize so that the probabilities for each timestep sum to 1
        # scale each sample by normalized probability
        # add together
        # serve

        # P(stream | sample) = P(sample | stream)P(stream) / P(sample)
        # P(sample | stream) = count(sample) / length(stream)
        # P(stream) = 1 / number_of_streams
        # P(sample) = 1 / number_of_samples

        p_stream = 1.0 / len(freqs)
        for row in freqs:
            p_sample = 1.0 / len(row)
            sample_counts = np.histogram(
