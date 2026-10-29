"""Reproducible signal-denoising experiment on synthetic speech-like signals.
This is NOT an ASR or real speech benchmark.
"""
import argparse, json
import numpy as np
from scipy.signal import butter, sosfiltfilt, stft, istft

def create_signal(sample_rate=16000, seconds=2.0, seed=21):
    rng = np.random.default_rng(seed)
    t = np.arange(int(sample_rate * seconds)) / sample_rate
    # Harmonic, amplitude-modulated proxy; not recorded human speech.
    voiced = sum(np.sin(2 * np.pi * f * t) / (i + 1) for i, f in enumerate([130,260,390,520,650,780]))
    envelope = (0.55 + 0.45 * np.sin(2 * np.pi * 3 * t)) * (np.sin(2 * np.pi * .8 * t)**2)
    clean = voiced * envelope
    clean /= max(np.max(np.abs(clean)), 1e-12)
    noise = rng.normal(size=len(t))
    # Low-frequency rumble and high-frequency hiss
    noise += .5 * np.sin(2 * np.pi * 60 * t)
    return clean, noise

def snr_db(clean, estimate):
    power = np.mean(clean**2)
    error = np.mean((clean-estimate)**2)
    return float(10*np.log10((power+1e-12)/(error+1e-12)))

def mix_at_snr(clean, noise, target_snr):
    scale = np.sqrt(np.mean(clean**2)/(np.mean(noise**2)*10**(target_snr/10)))
    return clean+scale*noise

def bandpass(audio, sr):
    sos=butter(4,[100,1200],btype='bandpass',fs=sr,output='sos')
    return sosfiltfilt(sos,audio)

def spectral_gate(audio, sr, threshold=1.5):
    _, _, z=stft(audio, fs=sr, nperseg=512, noverlap=384)
    noise_est=np.median(np.abs(z),axis=1,keepdims=True)
    gain=np.clip((np.abs(z)-threshold*noise_est)/(np.abs(z)+1e-12),0,1)
    _, out=istft(z*gain,fs=sr,nperseg=512,noverlap=384)
    return out[:len(audio)]

def run(seed=21, targets=(-5,0,5,10)):
    clean, noise=create_signal(seed=seed)
    rows=[]
    for target in targets:
        mixture=mix_at_snr(clean,noise,target)
        baseline=snr_db(clean,mixture)
        for name,processed in [('bandpass',bandpass(mixture,16000)),('spectral_gate',spectral_gate(mixture,16000))]:
            result=snr_db(clean,processed)
            rows.append({'target_input_snr_db':target,'method':name,'input_snr_db':round(baseline,3),'output_snr_db':round(result,3),'delta_snr_db':round(result-baseline,3)})
    return rows

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--seed',type=int,default=21); parser.add_argument('--output',default='results.json')
    args=parser.parse_args(); rows=run(seed=args.seed)
    with open(args.output,'w') as file:json.dump({'dataset':'synthetic harmonic proxy, not actual speech','seed':args.seed,'results':rows},file,indent=2)
    print(json.dumps(rows,indent=2))
