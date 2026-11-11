## Table 9. Per-task comparison of the stack with the best baseline (seed 0; 1,000 case-level bootstrap resamples)

| Protocol | Task | Best baseline | AUC stack | AUC baseline | Δ AUC | 95% case-bootstrap CI of Δ | Bootstrap p |
|---|---|---|---|---|---|---|---|
| BENCHMARK | BPIC12-acc | CatBoost | 0.701 | 0.697 | +0.0042 | [-0.0012, +0.0095] | 0.134 |
| BENCHMARK | BPIC12-can | RF | 0.724 | 0.734 | -0.0094 | [-0.0240, +0.0062] | 0.204 |
| BENCHMARK | BPIC12-dec | XGB | 0.590 | 0.608 | -0.0174 | [-0.0387, +0.0040] | 0.134 |
| BENCHMARK | BPIC17-acc | LGBM | 0.900 | 0.899 | +0.0001 | [-0.0004, +0.0006] | 0.618 |
| BENCHMARK | BPIC17-can | LGBM | 0.864 | 0.864 | +0.0002 | [-0.0007, +0.0012] | 0.598 |
| BENCHMARK | BPIC17-ref | LGBM | 0.855 | 0.855 | +0.0007 | [-0.0013, +0.0027] | 0.526 |
| BENCHMARK | Sepsis-1 | LR | 0.377 | 0.504 | -0.1267 | [-0.3143, +0.0543] | 0.158 |
| BENCHMARK | Sepsis-2 | LR | 0.818 | 0.886 | -0.0671 | [-0.1599, +0.0242] | 0.156 |
| BENCHMARK | Sepsis-3 | LR | 0.725 | 0.704 | +0.0216 | [-0.0720, +0.1204] | 0.688 |
| BENCHMARK | Traffic | LR | 0.795 | 0.793 | +0.0018 | [+0.0001, +0.0034] | 0.042 |
| STRICT | BPIC12-acc | CatBoost | 0.552 | 0.574 | -0.0226 | [-0.0497, +0.0037] | 0.104 |
| STRICT | BPIC17-acc | LGBM | 0.681 | 0.680 | +0.0005 | [-0.0009, +0.0020] | 0.464 |
| STRICT | Sepsis-1 | LR | 0.508 | 0.528 | -0.0201 | [-0.1726, +0.1252] | 0.790 |
| STRICT | Traffic | Transformer | 0.793 | 0.791 | +0.0017 | [+0.0010, +0.0022] | <0.001 |
