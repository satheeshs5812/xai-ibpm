- Hardware: 2 vCPU, 7 GB RAM, no GPU. All models on CPU; every training process used 1 thread (n_jobs/thread_count = 1, torch 1 thread); up to 3 processes ran concurrently, so per-task wall-clock times include contention.
- OS / Python: Linux-6.18.44-fc-v185-x86_64-with-glibc2.39, Python 3.13.18
- Libraries: scikit-learn 1.9.1, lightgbm 4.7.0, xgboost 3.4.1, catboost 1.2.10, optuna 5.0.0, shap 0.54.1, lime 0.2.0.1, torch 2.15.0, numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, matplotlib 3.11.2, scikit-posthocs 0.17.1
- Seeds: training seeds 0–4 for all stochastic models (GBMs, RF, LSTM, Transformer, stack); LR deterministic. Optuna TPE seed 0; subsampling seed 0 (fit) / 1 (validation); bootstrap seed 0 (AUC CIs) / 1 (prefix bands); XAI sampling seed 0.
- Total wall-clock for the whole v2 round (prep, tuning, training, evaluation, XAI, figures): about 2 h on this machine (sum of per-task process times below exceeds this because of parallel queues).
- Per-task process runtimes (s):

| protocol | task | gbm_tuning_and_training_s | deep_models_s | evaluation_s |
|---|---|---|---|---|
| benchmark | bpic2012_accepted | 425 | 315 | 75 |
| benchmark | bpic2012_cancelled | 461 | 321 | 78 |
| benchmark | bpic2012_declined | 735 | 334 | 73 |
| benchmark | bpic2017_accepted | 563 | 181 | 215 |
| benchmark | bpic2017_cancelled | 1306 | 327 | 101 |
| benchmark | bpic2017_refused | 2487 | 271 | 199 |
| benchmark | sepsis_cases_1 | 106 | 54 | 23 |
| benchmark | sepsis_cases_2 | 180 | 40 | 23 |
| benchmark | sepsis_cases_3 | 169 | 68 | 26 |
| benchmark | traffic_fines_1 | 646 | 455 | 180 |
| strict | bpic2012_accepted | 329 | 152 | 36 |
| strict | bpic2017_accepted | 1124 | 272 | 105 |
| strict | sepsis_cases_1 | 126 | 29 | 15 |
| strict | traffic_fines_1 | 643 | 488 | 135 |
