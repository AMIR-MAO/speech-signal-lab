# Speech Signal Lab | controlled denoising research prototype

[![Research stage](https://img.shields.io/badge/stage-synthetic%20proof%20of%20concept-orange)](#limitations)

A **reproducible experimental comparison** of two digital signal processing approaches on *synthetic speech-like harmonic proxies*, extended with a separate evaluator for user-provided paired WAV files. Designed to demonstrate Python, signal processing, experimental controls, uncertainty quantification and responsible reporting. This is **not** a speech recognition system and **not** a real-world speech accuracy benchmark.

## Research question and methods

> Under controlled additive noise, what is the change in reference-based sample SNR when applying a Butterworth band-pass filter or an STFT spectral gate?

- **Independent variable:** preprocessing method (`no_processing`, `bandpass`, `spectral_gate`)
- **Controlled variables:** clean reference, injected noise draw, target input SNR (-5, 0, 5, 10 dB), sampling rate 16 kHz
- **Replicates:** independent NumPy random seeds (20 by default)
- **Primary metric:** `delta_snr_db = output_snr_db - input_snr_db`; negative values count as regressions
- **Uncertainty:** percentile bootstrap 95% interval over random-seed replicates, not audio samples
- **Baseline:** identity/no processing, to ensure an honest comparison

## Reproduce

Python 3.11+:

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python src/research.py --seeds 20 --output-dir output
```

Expected local outputs: `output/trial_results.csv` and `output/summary.json`. The `output/` folder is intentionally ignored by Git. A historical single-seed output is in `results.json` for comparison with the original prototype.

To compare a **consented, nonconfidential** clean and noisy WAV pair:

```bash
python src/evaluate_wav.py clean.wav noisy.wav --output output/paired_eval.json
```

The files must share sample rate and duration and be aligned sample-by-sample. Optional WAV evaluation measures SNR only, not intelligibility.

## Implementation

- `src/speech_lab.py`: original synthetic generator and DSP baselines, retained intact
- `src/research.py`: controlled multi-seed evaluation and uncertainty estimates
- `src/evaluate_wav.py`: user-supplied aligned WAV evaluation
- `tests/`: deterministic signal, dataset validation, output shape, baseline and uncertainty tests
- `.github/workflows/ci.yml`: pytest across supported Python versions once copied into its own GitHub repository
- `docs/EXPERIMENT_PROTOCOL.md`: design, limitations, next milestones

## Limitations

1. The synthetic harmonic signal is not natural speech; **no WER, model accuracy, or speech intelligibility has been demonstrated**.
2. STFT-gate noise estimation from a noisy mixture can be biased when speech energy is present.
3. SNR depends on time alignment; paired WAV files must be aligned before evaluation.
4. Bootstrap intervals describe the seed distribution under this simulation, not a broad population of human voices.
5. Human-speech benchmarking, licensed open datasets, and pinned ASR baselines are a next step, not a completed result.

## Ethics and reproducibility

No employer recordings, personal information or proprietary code are used. This repository is a new, standalone, AI-assisted portfolio implementation, not a release of prior employers' systems. Review the design and code before claiming individual expertise.
