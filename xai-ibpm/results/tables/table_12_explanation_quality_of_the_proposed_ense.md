## Table 12. Explanation quality of the proposed ensemble (BENCHMARK, 100 stratified test prefixes; LIME stability on 30)

| Criterion | BPIC12-acc | BPIC17-acc | Sepsis-2 | Traffic |
|---|---|---|---|---|
| SHAP stability: input perturbation | 0.98 ± 0.04 | 0.89 ± 0.07 | 0.92 ± 0.09 | 0.95 ± 0.09 |
| SHAP stability: across 5 training seeds | 0.58 ± 0.12 | 0.60 ± 0.10 | 0.43 ± 0.12 | 0.84 ± 0.11 |
| LIME stability: input perturbation | 0.95 ± 0.09 | 0.80 ± 0.12 | 0.55 ± 0.11 | 0.51 ± 0.13 |
| LIME stability: across sampling seeds | 0.98 ± 0.08 | 0.68 ± 0.09 | 0.48 ± 0.08 | 0.30 ± 0.08 |
| SHAP–LIME agreement: top-5 Jaccard | 0.12 ± 0.04 | 0.51 ± 0.15 | 0.14 ± 0.07 | 0.29 ± 0.18 |
| SHAP–LIME (no discretisation): top-5 Jaccard | 0.28 ± 0.17 | 0.45 ± 0.29 | 0.22 ± 0.14 | 0.60 ± 0.14 |
| SHAP–LIME agreement: Kendall's τ | 0.40 ± 0.13 | 0.70 ± 0.09 | 0.56 ± 0.11 | 0.62 ± 0.06 |
| SHAP–LIME sign agreement on shared features | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 |
| Runtime ensemble TreeSHAP (ms / instance) | 19 | 18 | 20 | 17 |
| Runtime LIME, 1,000 samples (ms / instance) | 167 | 234 | 224 | 182 |
