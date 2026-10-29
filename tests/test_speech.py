import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from speech_lab import create_signal,snr_db,mix_at_snr,spectral_gate,bandpass,run

def test_deterministic():
    a,b=create_signal(); c,d=create_signal(); assert np.array_equal(a,c) and np.array_equal(b,d)
def test_snr_target():
    clean,noise=create_signal(); noisy=mix_at_snr(clean,noise,0); assert abs(snr_db(clean,noisy)) < 0.01
def test_shapes():
    c,n=create_signal(); assert len(spectral_gate(c,16000))==len(c); assert len(bandpass(c,16000))==len(c)
def test_results():
    assert len(run())==8
