import numpy as np
import subprocess as sp
from threading import Thread

n_samples = 44100

proc = sp.Popen(['cat'], stdin=sp.PIPE, stdout=sp.PIPE)
out_arr = np.ones(n_samples, dtype=np.int16)

def reader():
    in_arr = np.fromfile(proc.stdout, np.int16, n_samples)
    assert np.all(np.equal(in_arr, out_arr))

reader_thread = Thread(target=reader)
reader_thread.start()

out_arr.tofile(proc.stdin)
