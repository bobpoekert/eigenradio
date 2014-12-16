import numpy.fft as fft
import numpy as np

def merge_streams(sample_streams):
    """Takes an sequence of sequences of numpy arrays representing audio samples
       and produces a sequence of numpy arrays representing audio samples which are
       the product of the input samples at each timestep scaled by discriminativeness
    """
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
        res = None
        for row in freqs:
            p_sample = 1.0 / len(row)
            distinct_samples = np.unique(row)
            if len(distinct_samples) == len(row):
                counts = np.ones(len(distnct_samples))
            else:
                counts, bin_edges = np.histogram(row, buckets=len(distinct_samples), density=False)

            p_sample_given_stream = counts / len(counts)
            p_stream_given_sample = (p_sample_given_stream * p_stream) / p_sample

            normed_p_sample_given_stream = p_sample_given_stream / np.sum(p_sample_given_stream)
            scaled_row = row * normed_p_sample_given_stream

            if res is None:
                res = scaled_row
            else:
                res = res * scaled_row

        yield fft.ifft(res)
