## Table 16. Ablation of the proposed model (mean over tasks; B = BENCHMARK, S = STRICT)

| Variant | AUC (B) | Brier (B) | ECE (B) | Log-loss (B) | Automation (B) | AUC (S) | ECE (S) | Automation (S) |
|---|---|---|---|---|---|---|---|---|
| **Full model (tuned stack + monotone calibrator selection)** | 0.739 | 0.139 | 0.053 | 0.434 | 0.584 | 0.634 | 0.057 | 0.401 |
| Without post-hoc calibrator | 0.739 | 0.141 | 0.057 | 0.438 | 0.593 | 0.631 | 0.059 | 0.415 |
| Without Transformer base model | 0.735 | 0.139 | 0.051 | 0.435 | 0.571 | 0.631 | 0.061 | 0.420 |
| Without hyper-parameter tuning (default GBMs, 1 seed) | 0.742 | 0.136 | 0.043 | 0.422 | 0.521 | 0.613 | 0.061 | 0.430 |
| Single best tuned GBM + isotonic (no stacking) | 0.734 | 0.145 | 0.061 | 0.516 | 0.473 | 0.626 | 0.073 | 0.324 |
| Single tuned LightGBM, uncalibrated | 0.723 | 0.140 | 0.061 | 0.439 | 0.580 | 0.604 | 0.069 | 0.393 |
| Single Transformer | 0.710 | 0.146 | 0.046 | 0.450 | 0.543 | 0.607 | 0.070 | 0.405 |
