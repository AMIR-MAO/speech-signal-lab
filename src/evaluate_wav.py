"""Optional paired-WAV evaluation for user-provided nonconfidential audio.

Works with open, user-owned clean speech and corrupted counterparts.
Mono or stereo 16-bit PCM WAV at the SAME sample rate, with matching lengths.
Produces audio SNR only, never an ASR accuracy claim.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from speech_lab import snr_db, bandpass, spectral_gate

def _mono_float(p):
    if not Path(p).is_file():
        raise ValueError(f"Missing WAV file: {p}")
    sr, data = wavfile.read(p)
    if data.dtype.kind == 'i':
        values = data.astype(np.float64) / float(max(abs(np.iinfo(data.dtype).min), np.iinfo(data.dtype).max))
    elif data.dtype.kind == 'f':
        values = data.astype(np.float64)
    else:
        raise ValueError('Expected integer PCM or floating-point WAV')
    if values.ndim == 2:
        values = values.mean(axis=1)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError('Invalid WAV array')
    return sr, values

def evaluate(clean_file, noisy_file):
    sr1, clean = _mono_float(clean_file)
    sr2, noisy = _mono_float(noisy_file)
    if sr1 != sr2 or len(clean) != len(noisy) or not len(clean):
        raise ValueError('Clean/noisy audio must match in sample rate and length')
    if not (sr1 > 2400):
        raise ValueError('Sample rate is too low for the configured bandpass')
    baseline = snr_db(clean, noisy)
    out = {'clean_file': str(clean_file), 'noisy_file': str(noisy_file),
           'sample_rate_hz': sr1, 'duration_s': round(len(clean)/sr1, 4),
           'input_snr_db': round(baseline, 3), 'methods': {}}
    for name, fun in [('bandpass', bandpass), ('spectral_gate', spectral_gate)]:
        output = snr_db(clean, fun(noisy, sr1))
        out['methods'][name] = {'output_snr_db': round(output, 3),
                                'delta_snr_db': round(output - baseline, 3)}
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('clean', type=Path); ap.add_argument('noisy', type=Path)
    ap.add_argument('--output', type=Path); a=ap.parse_args()
    result=evaluate(a.clean,a.noisy); text=json.dumps(result,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n')
    print(text)

if __name__=='__main__': main()
