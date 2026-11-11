## Table 8. Average ranks, mean AUC and pairwise tests of the stack vs each baseline

| Model | Avg rank (B) | Wins (B) | Mean AUC (B) | Δ AUC stack − model (B) | Wilcoxon p, Holm (B) | Avg rank (S) | Mean AUC (S) | Δ AUC stack − model (S) |
|---|---|---|---|---|---|---|---|---|
| LR | 5.30 | 3 | 0.678 | +0.0610 | 0.480 | 6.25 | 0.579 | +0.0545 |
| RF | 5.00 | 1 | 0.728 | +0.0116 | 0.336 | 5.50 | 0.602 | +0.0315 |
| XGB | 4.10 | 1 | 0.734 | +0.0053 | 0.480 | 4.50 | 0.609 | +0.0252 |
| LGBM | 4.60 | 1 | 0.723 | +0.0165 | 0.098 | 4.75 | 0.604 | +0.0295 |
| CatBoost | 4.00 | 0 | 0.739 | +0.0008 | 0.480 | 2.75 | 0.637 | -0.0036 |
| LSTM | 5.50 | 0 | 0.710 | +0.0296 | 0.041* | 6.00 | 0.601 | +0.0331 |
| Transformer | 5.30 | 0 | 0.710 | +0.0288 | 0.041* | 4.50 | 0.607 | +0.0263 |
| **Stack (proposed)** | **2.20** | **4** | **0.739** | — | — | **1.75** | 0.634 | — |

Friedman (BENCHMARK): χ² = 13.73, p = 0.056; Nemenyi CD = 3.32  
Friedman (STRICT): χ² = 11.33, p = 0.125; Nemenyi CD = 5.25  
