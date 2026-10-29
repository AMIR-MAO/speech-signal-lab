import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from scipy.io import wavfile
from research import experiment,summarize
from evaluate_wav import evaluate

def test_paired_experiment_and_baseline():
    rows=experiment(seeds=[1,2],targets=[-5,5])
    assert len(rows)==12
    assert all(abs(r['delta_snr_db'])<1e-9 for r in rows if r['method']=='no_processing')
    assert rows == experiment(seeds=[1,2],targets=[-5,5])

def test_ci_and_no_unsupported_claims():
    result=summarize(experiment(seeds=[1,2,3],targets=[0]),bootstrap_samples=200)
    assert len(result)==3
    assert all(r['n_replicates']==3 and r['ci95_low_db']<=r['mean_delta_snr_db']<=r['ci95_high_db'] for r in result)

def test_wav_pair_evaluation(tmp_path):
    sample_rate=16000
    t=np.arange(sample_rate)/sample_rate
    clean=(np.sin(2*np.pi*440*t)*14000).astype(np.int16)
    noisy=(clean.astype(np.int32)+np.random.default_rng(0).integers(-800,800,len(clean))).clip(-32768,32767).astype(np.int16)
    a=tmp_path/'clean.wav';b=tmp_path/'noisy.wav'
    wavfile.write(a,sample_rate,clean);wavfile.write(b,sample_rate,noisy)
    r=evaluate(a,b)
    assert r['sample_rate_hz']==sample_rate
    assert len(r['methods'])==2
    with pytest.raises(ValueError):evaluate(a, tmp_path/'missing.wav')
