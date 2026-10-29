# Experiment protocol (v0.2)

**Question:** Do the specified band-pass and spectral gate improve waveform-level SNR in the synthetic proxy relative to no processing?

## Research design

1. Generate one fixed-length harmonic amplitude-modulated reference and a repeatable Gaussian/tonal noise sample for each seed.
2. Generate additive mixtures at -5, 0, 5 and 10 dB with the same clean/noise pair within the seed.
3. Run three conditions on the same mixture: identity, 4th order Butterworth band-pass, STFT magnitude gate.
4. Measure baseline and post-filter error power relative to the known reference.
5. For each method x input-SNR group, bootstrap means by resampling independent *seed* trials, using a dedicated fixed RNG seed.
6. Record regressions as well as improvements. Do **not** select a winning technique based on the best seed alone.

## Threats to validity

- Synthetic voiced signals oversimplify phonemes, spectral dynamics, pauses and real background noise.
- Processed-waveform SNR != ASR word-error-rate and does not guarantee intelligibility.
- Band-pass width 100–1200 Hz may discard informative speech frequency bands.
- Filters use full-utterance information; latency is not measured and real-time suitability is **not** established.
- Basic bootstrap ignores variation in speakers, microphones and acoustic scenes.

## Next validation gate

Before claiming real speech improvements, use public licensed real recordings (e.g. a permitted subset of LibriSpeech and separately sourced noise), document URLs and license, pre-register the dataset split, run pinned preprocessing and ASR models, compute WER/CER with confidence intervals and publish failure cases. Do not publish third-party recordings or model weights without licence checks.
