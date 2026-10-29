# Synthetic SNR study: observed results

Experiment: 20 independent noise seeds, 4 target input SNR levels, 3 methods, 240 total trials. Metric: change in sample-level SNR relative to a synthetic harmonic proxy clean signal, with 95% percentile-bootstrap intervals across seeds.

**Representative findings:** At -5 dB input SNR, the band-pass method improved mean SNR by +9.52 dB (95% bootstrap CI +9.48 to +9.56), while spectral gating improved it by +7.48 dB (+7.41 to +7.55). At +10 dB input SNR, the spectral gate **degraded** mean SNR by -6.35 dB (-6.38 to -6.33). Reported negative results are intentionally retained.

This is **not** evidence of reduced word-error-rate, human speech intelligibility or model transcription accuracy. The narrow CIs reflect synthetic seed replicates, not generalisation to speakers/noise environments. See `../EXPERIMENT_PROTOCOL.md`.

Reproduce with `python src/research.py --seeds 20 --output-dir output`. The attached JSON includes all group summaries; raw trial CSV is a local artifact (not published by default).
