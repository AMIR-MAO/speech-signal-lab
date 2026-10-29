"""Research-grade reporting for the existing synthetic signal denoising experiment.

Design: independent random seeds are replicates, controlled input SNRs are paired
within a seed, and each method uses the identical mixture for fair comparison.
This module makes NO claim about human speech intelligibility or ASR accuracy.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from speech_lab import create_signal, mix_at_snr, snr_db, bandpass, spectral_gate

METHODS = ('no_processing', 'bandpass', 'spectral_gate')

def experiment(seeds=range(10, 30), targets=(-5, 0, 5, 10), sample_rate=16000):
    rows = []
    for seed in seeds:
        clean, noise = create_signal(sample_rate=sample_rate, seed=int(seed))
        for target in targets:
            noisy = mix_at_snr(clean, noise, target)
            input_snr = snr_db(clean, noisy)
            estimates = {
                'no_processing': noisy,
                'bandpass': bandpass(noisy, sample_rate),
                'spectral_gate': spectral_gate(noisy, sample_rate),
            }
            for name, estimate in estimates.items():
                output = snr_db(clean, estimate)
                rows.append({'seed': int(seed), 'target_snr_db': int(target),
                    'method': name, 'input_snr_db': round(input_snr, 6),
                    'output_snr_db': round(output, 6),
                    'delta_snr_db': round(output - input_snr, 6)})
    return rows

def summarize(rows, bootstrap_samples=2000, random_seed=2026):
    """Bootstrap CI resamples seed-level replicates, not correlated audio frames."""
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r['target_snr_db'], r['method'])].append(r['delta_snr_db'])
    rng = np.random.default_rng(random_seed)
    summary = []
    for (target, method), values in sorted(grouped.items()):
        x = np.array(values, dtype=float)
        if not len(x):
            continue
        if len(x) == 1:
            low = high = float(x[0])
        else:
            idx = rng.integers(0, len(x), size=(bootstrap_samples, len(x)))
            means = x[idx].mean(axis=1)
            low, high = map(float, np.quantile(means, [0.025, 0.975]))
        summary.append({'target_snr_db': target, 'method': method,
            'n_replicates': int(len(x)), 'mean_delta_snr_db': round(float(x.mean()), 4),
            'ci95_low_db': round(low, 4), 'ci95_high_db': round(high, 4)})
    return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, default=20)
    parser.add_argument('--output-dir', type=Path, default=Path('output'))
    args = parser.parse_args()
    if args.seeds < 2:
        parser.error('--seeds must be >= 2 to estimate uncertainty')
    rows = experiment(range(10, 10 + args.seeds))
    summary = summarize(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / 'trial_results.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    report = {'data_type': 'synthetic harmonic proxy (NOT real speech)',
        'research_question': 'Does denoising improve sample-level SNR in this controlled proxy?',
        'seeds': args.seeds, 'conditions': list(sorted(set(r['target_snr_db'] for r in rows))),
        'methods': list(METHODS), 'metric': 'delta SNR (dB)',
        'uncertainty': '95% percentile bootstrap CI across independent seeds',
        'limitations': ['No human speech', 'No WER/STOI/PESQ',
                        'Synthetic noise and signal may bias method comparisons'],
        'summary': summary}
    (args.output_dir / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'trials': len(rows), 'groups': len(summary), 'directory': str(args.output_dir)}))

if __name__ == '__main__':
    main()
