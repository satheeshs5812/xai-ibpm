# Results summary: tuned, state-of-the-art models, two evaluation protocols, statistics and governance

All numbers in this file are read from the CSV files in `results/` produced by the scripts in `src/` on the original 4TU.ResearchData event logs (SHA-256 checksums in `data/README.md`). Nothing was synthesised, adjusted or copied from the literature. mean ± sd is over 5 training seeds (0–4) unless stated otherwise; LR is deterministic (1 run).

## 1. Prediction tasks and dataset statistics

Labels re-implement the preprocessing scripts of irhete/predictive-monitoring-benchmark (Teinemaa et al., TKDD 2019), downloaded from raw.githubusercontent.com and kept in `teinemaa_ref/` for reference. label = 1 is always the benchmark "deviant" class. `sepsis_cases_3` (Release A) is written by the benchmark script as `sepsis_cases_4.csv`; we use the paper's name.

Sanity check against the benchmark: our labelled logs give BPIC2012 4,685 cases (K = 40), BPIC2017 31,413 cases (K = 20), Sepsis 782 cases (K = 29 / 13 / 22 for tasks 1 / 2 / 3), Traffic fines 129,615 cases after removing incomplete cases (K = 10); these are the case counts and prefix caps produced by the benchmark rules.

| protocol | task | label_definition | cases | events | activities | variants | mean_case_length | max_case_length | positive_case_ratio | max_prefix_len_K | train_cases | test_cases | fit_prefixes_before_subsample | fit_prefixes_used | val_prefixes_used | test_prefixes | test_positive_prefix_ratio | n_features_agg | n_features_agg_index | split_timestamp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | BPIC2012: last offer event is O_ACCEPTED | 4685 | 186693 | 36 | 3790 | 39.8500 | 175 | 0.4788 | 40 | 3748 | 937 | 93128 | 79992 | 18714 | 30637 | 0.5539 | 134 | 164 | 2012-01-27 14:58:46.061000+00:00 |
| benchmark | bpic2012_cancelled | BPIC2012: last offer event is O_CANCELLED | 4685 | 186693 | 36 | 3790 | 39.8500 | 175 | 0.3501 | 40 | 3748 | 937 | 93128 | 79992 | 18714 | 30637 | 0.2554 | 134 | 164 | 2012-01-27 14:58:46.061000+00:00 |
| benchmark | bpic2012_declined | BPIC2012: last offer event is O_DECLINED | 4685 | 186693 | 36 | 3790 | 39.8500 | 175 | 0.1712 | 40 | 3748 | 937 | 93128 | 79992 | 18714 | 30637 | 0.1907 | 134 | 164 | 2012-01-27 14:58:46.061000+00:00 |
| benchmark | bpic2017_accepted | BPIC2017: last Offer-origin event is O_Accepted | 31413 | 1198366 | 26 | 15846 | 38.1500 | 180 | 0.4072 | 20 | 25130 | 6283 | 394433 | 79993 | 49983 | 124815 | 0.4036 | 247 | 277 | 2016-10-18 11:53:00.635000+00:00 |
| benchmark | bpic2017_cancelled | BPIC2017: last Offer-origin event is O_Cancelled | 31413 | 1198366 | 26 | 15846 | 38.1500 | 180 | 0.4744 | 20 | 25130 | 6283 | 394433 | 79993 | 49983 | 124815 | 0.4684 | 247 | 277 | 2016-10-18 11:53:00.635000+00:00 |
| benchmark | bpic2017_refused | BPIC2017: last Offer-origin event is O_Refused | 31413 | 1198366 | 26 | 15846 | 38.1500 | 180 | 0.1184 | 20 | 25130 | 6283 | 394433 | 79993 | 49983 | 124815 | 0.1279 | 247 | 277 | 2016-10-18 11:53:00.635000+00:00 |
| benchmark | sepsis_cases_1 | Sepsis: Return ER within 28 days of previous event | 782 | 13120 | 15 | 709 | 16.7800 | 185 | 0.1419 | 29 | 625 | 157 | 7760 | 7760 | 1796 | 2493 | 0.1087 | 214 | 244 | 2014-10-26 19:21:00+00:00 |
| benchmark | sepsis_cases_2 | Sepsis: Admission IC occurs | 782 | 10924 | 15 | 707 | 13.9700 | 60 | 0.1368 | 13 | 625 | 157 | 5821 | 5821 | 1436 | 1859 | 0.1022 | 212 | 242 | 2014-10-26 19:21:00+00:00 |
| benchmark | sepsis_cases_3 | Sepsis: Release A occurs (benchmark script output sepsis_cases_4.csv) | 782 | 12463 | 15 | 709 | 15.9400 | 185 | 0.8581 | 22 | 625 | 157 | 7050 | 7050 | 1655 | 2259 | 0.8123 | 214 | 244 | 2014-10-26 19:21:00+00:00 |
| benchmark | traffic_fines_1 | Traffic fines: Send for Credit Collection occurs | 129615 | 460556 | 10 | 200 | 3.5500 | 20 | 0.4553 | 10 | 103652 | 25923 | 291080 | 80000 | 50000 | 88530 | 0.4719 | 216 | 246 | 2009-06-25 22:00:00+00:00 |
| strict | bpic2012_accepted | BPIC2012: last offer event is O_ACCEPTED | 4685 | 133028 | 28 | 2094 | 28.3900 | 164 | 0.4788 | 20 | 3748 | 937 | 55965 | 55965 | 13362 | 17704 | 0.5215 | 121 | 151 | 2012-01-27 14:58:46.061000+00:00 |
| strict | bpic2017_accepted | BPIC2017: last Offer-origin event is O_Accepted | 31413 | 1057567 | 20 | 14240 | 33.6700 | 175 | 0.4072 | 20 | 25130 | 6283 | 384900 | 79985 | 49998 | 121335 | 0.4108 | 223 | 253 | 2016-10-18 11:53:00.635000+00:00 |
| strict | sepsis_cases_1 | Sepsis: Return ER within 28 days of previous event | 782 | 13120 | 15 | 709 | 16.7800 | 185 | 0.1419 | 20 | 625 | 157 | 7268 | 7268 | 1721 | 2324 | 0.1089 | 209 | 239 | 2014-10-26 19:21:00+00:00 |
| strict | traffic_fines_1 | Traffic fines: Send for Credit Collection occurs | 150370 | 502441 | 10 | 205 | 3.3400 | 20 | 0.3925 | 10 | 120212 | 30074 | 317665 | 79998 | 50000 | 96118 | 0.4256 | 216 | 246 | 2009-07-02 22:00:00+00:00 |


"events"/"cases" refer to the labelled log after case filtering and after the protocol's truncation. fit/val prefixes are after whole-case subsampling (caps: 80,000 fit prefixes, 50,000 validation prefixes); test prefixes are never subsampled.

## 2. The two evaluation protocols

| aspect | BENCHMARK (literature-comparable) | STRICT (leakage-free) |
|---|---|---|
| tasks | all 10 tasks | bpic2012_accepted, bpic2017_accepted, sepsis_cases_1, traffic_fines_1 |
| BPIC2012 truncation | none (as in the benchmark script; outcome events O_ACCEPTED/O_DECLINED/O_CANCELLED and A_* decision events stay in the prefixes if they occur within K events) | cut before first O_ACCEPTED/O_DECLINED/O_CANCELLED or A_APPROVED/A_REGISTERED/A_ACTIVATED/A_DECLINED/A_CANCELLED (COMPLETE) |
| BPIC2017 truncation | none (as in the benchmark script) | cut before first O_Accepted/O_Refused/O_Cancelled/A_Pending/A_Denied/A_Cancelled |
| Sepsis truncation | cut before the label activity (Return ER / Admission IC / Release A), as in the script | same (sepsis_cases_1 only) |
| Traffic | cases whose last event is "Send Fine" removed (incomplete); cut before Send for Credit Collection | no incomplete-case removal; cut before Send for Credit Collection |
| prefix cap K | traffic 10; BPIC2017 min(20, q90 of positive case length); others min(40, q90 positive length) → 40 / 20 / 29 / 13 / 22 / 10 | fixed 20 (traffic 10) |
| inter-case feature open_cases | included (benchmark; note it uses each case's end time, i.e. future information) | excluded (not observable at prediction time) |
| everything else | identical: temporal 80/20 split with train events after the first test start discarded; train split again 80/20 temporally into fit / validation; validation split by case start into part A (first half) and part B (second half); same encoders and models | identical |

Deviations from the benchmark code that apply to both protocols: categorical vocabularies are fitted on the fit split only (benchmark: whole log); hyper-parameters are tuned on a temporal validation split (benchmark: random 3-fold CV inside train); one model for all prefix lengths (no bucketing); BPIC2012/2017 benchmark tasks are encoded once per log (labels differ only).

## 3. Models, encodings and tuning

- **Encodings.** (a) `agg`: Teinemaa static+aggregation encoding — counts of every dynamic categorical level (activity, resource, and log-specific attributes), mean/max/min/sum/std of every dynamic numeric attribute (incl. time features hour, weekday, month, time since midnight, time since last event, time since case start, event number, and open_cases in BENCHMARK), static categorical one-hot and static numeric values. (b) `agg+index`: `agg` plus a lagged index encoding of the last 10 events (activity code, resource code, log time since previous event at lags 1..10; missing = NaN). Integer codes are frequency ranks on the fit split. For each GBM family the encoding was selected on the validation split with default hyper-parameters (table below), then tuned. LR and RF use `agg`. Prefix-length bucketing was not used (one model over all prefix lengths, prefix length is a feature).
- **Tuning.** Optuna 5.0 TPE sampler (seed 0), objective = AUC on the temporal validation split (never the test set), training on a ≤30,000-prefix whole-case subsample of the fit split, early stopping on validation (30 rounds, ≤600 trees). Trials: LightGBM 30, XGBoost 30, CatBoost 20 (CatBoost fewer for CPU budget); the first trial is the default configuration. Because XGBoost with the agg+index encoding was ~10× slower than expected on BPIC2017/traffic (28 min for 30 trials on bpic2017_refused), a wall-clock cap of 480 s per family study was added for the four tasks tuned last (benchmark traffic_fines_1 and bpic2017_cancelled, strict bpic2017_accepted and traffic_fines_1); the number of trials actually completed per task/family is given in the table (`n_trials_completed`). Final models: best parameters, full fit split, ≤1000 trees, early stopping (50) on validation, seeds 0–4.
  - LightGBM: learning_rate [0.02, 0.3] log; num_leaves [15, 255] log; min_child_samples [5, 200] log; subsample [0.5, 1]; colsample_bytree [0.3, 1]; reg_alpha, reg_lambda [1e-3, 10] log.
  - XGBoost (hist): learning_rate [0.02, 0.3] log; max_depth [3, 10]; min_child_weight [1, 50] log; subsample [0.5, 1]; colsample_bytree [0.3, 1]; gamma [1e-3, 5] log; reg_alpha, reg_lambda [1e-3, 10] log.
  - CatBoost (border_count 64): learning_rate [0.03, 0.3] log; depth [4, 8]; l2_leaf_reg [1, 30] log; bagging_temperature [0, 1]; random_strength [1e-3, 10] log.
- **Baselines.** LR (standardised, L2, C ∈ {0.01, 0.1, 1} chosen on validation); RF (150 trees, min_samples_leaf 5, max_features sqrt, max_samples 0.5).
- **Deep sequence models** (PyTorch, CPU). Input per event: activity embedding (16), resource embedding (8), standardised signed-log dynamic numeric attributes, static attributes repeated per step, linearly projected. Many-to-many training (one output per prefix position; BCE averaged over valid positions), Adam, batch 128 cases, gradient clipping 1.0, early stopping (patience 3) on validation prefix AUC, max 12 epochs (25 for logs with < 5,000 fit cases). LSTM: 1 layer, configs {h=64, lr 1e-3}, {h=128, lr 1e-3}, {h=64, lr 3e-3}. Transformer (ProcessTransformer-style, causal mask, learned positional embeddings, 4 heads, FF = 2d): {d=32, 1 layer, lr 1e-3}, {d=64, 2 layers, lr 1e-3}, {d=64, 2 layers, lr 3e-4}. Light tuning = best config on validation at seed 0, then seeds 0–4.
- **Proposed model ("Stack (proposed)").** Logistic-regression meta-learner (C = 1) on the log-odds of tuned LightGBM, XGBoost, CatBoost and Transformer, fitted on validation part A (base models never saw part A in training; part A was used for their early stopping/tuning). Post-hoc calibrator chosen per seed among none / Platt / isotonic / beta (Kull et al. 2017) / inductive Venn–Abers (merged p1/(1−p0+p1), evaluated on a 51-point score grid with linear interpolation) by grouped (by case) 5-fold cross-validated log-loss on out-of-fold meta predictions within part A. Validation part B is reserved for conformal calibration and deferral thresholds.

### Encoding selection, best hyper-parameters and validation AUC

| protocol | task | family | encoding | enc_val_auc_agg | enc_val_auc_agg_index | n_trials_completed | val_auc_default_trial | best_val_auc_tuning | final_iters | best_params | tuning_time_s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | CatBoost | agg+index | 0.6412 | 0.6593 | 20.0000 | 0.6593 | 0.6593 | [44, 79, 53, 38, 43] | {"learning_rate": 0.05, "depth": 6, "l2_leaf_reg": 3.0, "bagging_temperature": 1.0, "random_strength": 1.0} | 57.6261 |
| benchmark | bpic2012_accepted | LGBM | agg+index | 0.6523 | 0.6611 | 30.0000 | 0.6610 | 0.6645 | [29, 24, 32, 14, 35] | {"learning_rate": 0.0886, "num_leaves": 25, "min_child_samples": 95, "subsample": 0.8578, "colsample_bytree": 0.392, "reg_alpha": 0.0053, "reg_lambda": 0.0151} | 36.1208 |
| benchmark | bpic2012_accepted | XGB | agg | 0.6492 | 0.6483 | 30.0000 | 0.6491 | 0.6641 | [32, 26, 25, 11, 18] | {"learning_rate": 0.1959, "max_depth": 5, "min_child_weight": 7.8467, "subsample": 0.8099, "colsample_bytree": 0.4732, "gamma": 0.0826, "reg_alpha": 0.0949, "reg_lambda": 2.1435} | 41.2381 |
| benchmark | bpic2012_cancelled | CatBoost | agg | 0.6259 | 0.6222 | 20.0000 | 0.6259 | 0.6418 | [28, 5, 5, 4, 2] | {"learning_rate": 0.1062, "depth": 7, "l2_leaf_reg": 7.7688, "bagging_temperature": 0.5449, "random_strength": 0.0495} | 40.9102 |
| benchmark | bpic2012_cancelled | LGBM | agg | 0.6250 | 0.6144 | 30.0000 | 0.6250 | 0.6362 | [15, 7, 31, 20, 24] | {"learning_rate": 0.0558, "num_leaves": 31, "min_child_samples": 6, "subsample": 0.6919, "colsample_bytree": 0.9733, "reg_alpha": 0.0467, "reg_lambda": 0.0012} | 38.4030 |
| benchmark | bpic2012_cancelled | XGB | agg | 0.6276 | 0.6266 | 30.0000 | 0.6276 | 0.6342 | [5, 2, 12, 7, 13] | {"learning_rate": 0.2016, "max_depth": 8, "min_child_weight": 15.4079, "subsample": 0.6351, "colsample_bytree": 0.8941, "gamma": 0.0114, "reg_alpha": 0.0014, "reg_lambda": 0.0056} | 42.0218 |
| benchmark | bpic2012_declined | CatBoost | agg | 0.5893 | 0.5684 | 20.0000 | 0.5893 | 0.6249 | [13, 60, 11, 38, 19] | {"learning_rate": 0.0686, "depth": 6, "l2_leaf_reg": 10.7272, "bagging_temperature": 0.0602, "random_strength": 0.4646} | 39.0965 |
| benchmark | bpic2012_declined | LGBM | agg | 0.5844 | 0.5619 | 30.0000 | 0.5844 | 0.5851 | [18, 14, 18, 10, 16] | {"learning_rate": 0.1819, "num_leaves": 19, "min_child_samples": 47, "subsample": 0.6723, "colsample_bytree": 0.628, "reg_alpha": 0.0011, "reg_lambda": 0.0428} | 30.2016 |
| benchmark | bpic2012_declined | XGB | agg+index | 0.5738 | 0.5779 | 30.0000 | 0.5779 | 0.5941 | [15, 17, 26, 25, 34] | {"learning_rate": 0.0664, "max_depth": 4, "min_child_weight": 7.9167, "subsample": 0.5741, "colsample_bytree": 0.7451, "gamma": 0.0012, "reg_alpha": 0.0615, "reg_lambda": 0.0023} | 295.2670 |
| benchmark | bpic2017_accepted | CatBoost | agg+index | 0.8907 | 0.8912 | 20.0000 | 0.8912 | 0.8940 | [13, 8, 8, 10, 7] | {"learning_rate": 0.2561, "depth": 5, "l2_leaf_reg": 20.8203, "bagging_temperature": 0.3371, "random_strength": 0.6072} | 80.8111 |
| benchmark | bpic2017_accepted | LGBM | agg+index | 0.8925 | 0.8941 | 30.0000 | 0.8941 | 0.8944 | [61, 61, 38, 34, 32] | {"learning_rate": 0.0578, "num_leaves": 15, "min_child_samples": 7, "subsample": 0.9007, "colsample_bytree": 0.9582, "reg_alpha": 0.4522, "reg_lambda": 0.023} | 58.1316 |
| benchmark | bpic2017_accepted | XGB | agg | 0.8911 | 0.8872 | 30.0000 | 0.8911 | 0.8952 | [14, 10, 18, 34, 12] | {"learning_rate": 0.1529, "max_depth": 6, "min_child_weight": 8.8842, "subsample": 0.6991, "colsample_bytree": 0.8607, "gamma": 0.6747, "reg_alpha": 0.0065, "reg_lambda": 0.0163} | 87.7045 |
| benchmark | bpic2017_cancelled | CatBoost | agg+index | 0.8593 | 0.8593 | 20.0000 | 0.8593 | 0.8634 | [13, 11, 12, 10, 13] | {"learning_rate": 0.1537, "depth": 5, "l2_leaf_reg": 8.3542, "bagging_temperature": 0.2079, "random_strength": 0.0019} | 63.5007 |
| benchmark | bpic2017_cancelled | LGBM | agg | 0.8581 | 0.8578 | 30.0000 | 0.8581 | 0.8613 | [41, 23, 19, 17, 47] | {"learning_rate": 0.066, "num_leaves": 15, "min_child_samples": 5, "subsample": 0.5291, "colsample_bytree": 0.9585, "reg_alpha": 0.3586, "reg_lambda": 4.5367} | 96.0828 |
| benchmark | bpic2017_cancelled | XGB | agg+index | 0.8563 | 0.8566 | 6.0000 | 0.8566 | 0.8594 | [10, 7, 8, 13, 11] | {"learning_rate": 0.2719, "max_depth": 6, "min_child_weight": 22.1369, "subsample": 0.7644, "colsample_bytree": 0.6976, "gamma": 2.6531, "reg_alpha": 0.0019, "reg_lambda": 0.0022} | 547.4890 |
| benchmark | bpic2017_refused | CatBoost | agg+index | 0.8191 | 0.8224 | 20.0000 | 0.8224 | 0.8266 | [7, 8, 15, 47, 3] | {"learning_rate": 0.1225, "depth": 8, "l2_leaf_reg": 7.6146, "bagging_temperature": 0.5162, "random_strength": 0.0361} | 113.9189 |
| benchmark | bpic2017_refused | LGBM | agg | 0.8145 | 0.8059 | 30.0000 | 0.8145 | 0.8207 | [14, 13, 4, 15, 17] | {"learning_rate": 0.0242, "num_leaves": 19, "min_child_samples": 5, "subsample": 0.9163, "colsample_bytree": 0.8447, "reg_alpha": 3.0203, "reg_lambda": 8.2125} | 57.8701 |
| benchmark | bpic2017_refused | XGB | agg+index | 0.8100 | 0.8116 | 30.0000 | 0.8116 | 0.8253 | [7, 22, 19, 2, 14] | {"learning_rate": 0.0341, "max_depth": 5, "min_child_weight": 24.8223, "subsample": 0.5486, "colsample_bytree": 0.8866, "gamma": 0.0023, "reg_alpha": 8.0508, "reg_lambda": 0.0749} | 1674.1199 |
| benchmark | sepsis_cases_1 | CatBoost | agg | 0.6332 | 0.6131 | 20.0000 | 0.6332 | 0.7109 | [6, 29, 18, 7, 12] | {"learning_rate": 0.045, "depth": 7, "l2_leaf_reg": 11.7328, "bagging_temperature": 0.8095, "random_strength": 0.0022} | 17.5965 |
| benchmark | sepsis_cases_1 | LGBM | agg+index | 0.5759 | 0.6346 | 30.0000 | 0.6346 | 0.6777 | [3, 3, 4, 4, 9] | {"learning_rate": 0.038, "num_leaves": 15, "min_child_samples": 28, "subsample": 0.8062, "colsample_bytree": 0.6657, "reg_alpha": 0.0057, "reg_lambda": 0.019} | 23.5855 |
| benchmark | sepsis_cases_1 | XGB | agg | 0.6359 | 0.6308 | 30.0000 | 0.6359 | 0.6879 | [9, 13, 7, 5, 5] | {"learning_rate": 0.1392, "max_depth": 5, "min_child_weight": 46.2503, "subsample": 0.7779, "colsample_bytree": 0.4873, "gamma": 1.8944, "reg_alpha": 0.0014, "reg_lambda": 5.5251} | 20.5696 |
| benchmark | sepsis_cases_2 | CatBoost | agg | 0.9258 | 0.9197 | 20.0000 | 0.9258 | 0.9728 | [28, 14, 12, 37, 41] | {"learning_rate": 0.2889, "depth": 7, "l2_leaf_reg": 7.0896, "bagging_temperature": 0.5839, "random_strength": 0.0032} | 35.4289 |
| benchmark | sepsis_cases_2 | LGBM | agg | 0.9514 | 0.9450 | 30.0000 | 0.9477 | 0.9477 | [13, 6, 15, 16, 6] | {"learning_rate": 0.05, "num_leaves": 31, "min_child_samples": 20, "subsample": 0.8, "colsample_bytree": 0.8, "reg_alpha": 0.001, "reg_lambda": 0.001} | 20.0405 |
| benchmark | sepsis_cases_2 | XGB | agg+index | 0.9393 | 0.9490 | 30.0000 | 0.9490 | 0.9612 | [18, 10, 21, 37, 12] | {"learning_rate": 0.0276, "max_depth": 8, "min_child_weight": 1.7521, "subsample": 0.9723, "colsample_bytree": 0.6653, "gamma": 0.0342, "reg_alpha": 0.0114, "reg_lambda": 1.2501} | 71.5965 |
| benchmark | sepsis_cases_3 | CatBoost | agg | 0.6573 | 0.6169 | 20.0000 | 0.6573 | 0.6848 | [54, 42, 36, 8, 58] | {"learning_rate": 0.1857, "depth": 6, "l2_leaf_reg": 6.9035, "bagging_temperature": 0.9256, "random_strength": 0.0019} | 22.9622 |
| benchmark | sepsis_cases_3 | LGBM | agg+index | 0.7050 | 0.7075 | 30.0000 | 0.7260 | 0.7542 | [9, 3, 8, 5, 3] | {"learning_rate": 0.211, "num_leaves": 28, "min_child_samples": 26, "subsample": 0.5694, "colsample_bytree": 0.4334, "reg_alpha": 0.0013, "reg_lambda": 0.0056} | 21.3672 |
| benchmark | sepsis_cases_3 | XGB | agg+index | 0.6586 | 0.6831 | 30.0000 | 0.6831 | 0.7618 | [8, 17, 7, 11, 15] | {"learning_rate": 0.1865, "max_depth": 8, "min_child_weight": 30.6868, "subsample": 0.7331, "colsample_bytree": 0.3316, "gamma": 0.3297, "reg_alpha": 0.0232, "reg_lambda": 2.234} | 72.9064 |
| benchmark | traffic_fines_1 | CatBoost | agg+index | 0.7910 | 0.7928 | 20.0000 | 0.7928 | 0.7954 | [8, 9, 9, 34, 24] | {"learning_rate": 0.1327, "depth": 6, "l2_leaf_reg": 20.7614, "bagging_temperature": 0.9637, "random_strength": 0.0342} | 61.0682 |
| benchmark | traffic_fines_1 | LGBM | agg+index | 0.7875 | 0.7916 | 30.0000 | 0.7916 | 0.7943 | [18, 26, 2, 31, 35] | {"learning_rate": 0.1662, "num_leaves": 15, "min_child_samples": 18, "subsample": 0.5513, "colsample_bytree": 0.308, "reg_alpha": 0.0157, "reg_lambda": 0.0263} | 72.0772 |
| benchmark | traffic_fines_1 | XGB | agg | 0.7865 | 0.7863 | 30.0000 | 0.7865 | 0.7944 | [99, 22, 162, 154, 133] | {"learning_rate": 0.0843, "max_depth": 3, "min_child_weight": 5.5223, "subsample": 0.5628, "colsample_bytree": 0.4143, "gamma": 0.0519, "reg_alpha": 0.0825, "reg_lambda": 0.0063} | 187.7110 |
| strict | bpic2012_accepted | CatBoost | agg+index | 0.5614 | 0.5688 | 20.0000 | 0.5688 | 0.5814 | [32, 15, 51, 51, 34] | {"learning_rate": 0.0367, "depth": 4, "l2_leaf_reg": 16.9778, "bagging_temperature": 0.7782, "random_strength": 3.0203} | 42.0545 |
| strict | bpic2012_accepted | LGBM | agg+index | 0.5532 | 0.5691 | 30.0000 | 0.5691 | 0.5821 | [16, 21, 38, 33, 26] | {"learning_rate": 0.0719, "num_leaves": 41, "min_child_samples": 13, "subsample": 0.8324, "colsample_bytree": 0.5328, "reg_alpha": 0.0171, "reg_lambda": 0.0042} | 61.9815 |
| strict | bpic2012_accepted | XGB | agg | 0.5665 | 0.5549 | 30.0000 | 0.5665 | 0.5830 | [44, 27, 50, 84, 24] | {"learning_rate": 0.2175, "max_depth": 6, "min_child_weight": 27.995, "subsample": 0.7799, "colsample_bytree": 0.6853, "gamma": 0.883, "reg_alpha": 0.0023, "reg_lambda": 0.0111} | 47.0372 |
| strict | bpic2017_accepted | CatBoost | agg+index | 0.6596 | 0.6612 | 20.0000 | 0.6612 | 0.6653 | [46, 17, 50, 29, 49] | {"learning_rate": 0.1753, "depth": 4, "l2_leaf_reg": 21.3673, "bagging_temperature": 0.6107, "random_strength": 0.3198} | 38.4282 |
| strict | bpic2017_accepted | LGBM | agg+index | 0.6589 | 0.6627 | 30.0000 | 0.6627 | 0.6631 | [89, 62, 76, 23, 70] | {"learning_rate": 0.0459, "num_leaves": 20, "min_child_samples": 6, "subsample": 0.8989, "colsample_bytree": 0.6796, "reg_alpha": 4.4988, "reg_lambda": 1.9365} | 67.6192 |
| strict | bpic2017_accepted | XGB | agg+index | 0.6592 | 0.6623 | 16.0000 | 0.6623 | 0.6644 | [75, 101, 65, 60, 118] | {"learning_rate": 0.0422, "max_depth": 5, "min_child_weight": 5.8134, "subsample": 0.6048, "colsample_bytree": 0.9927, "gamma": 0.0038, "reg_alpha": 0.0107, "reg_lambda": 0.3433} | 506.2456 |
| strict | sepsis_cases_1 | CatBoost | agg | 0.6459 | 0.5787 | 20.0000 | 0.6459 | 0.6683 | [97, 9, 4, 132, 12] | {"learning_rate": 0.1757, "depth": 7, "l2_leaf_reg": 28.4473, "bagging_temperature": 0.938, "random_strength": 0.003} | 19.7830 |
| strict | sepsis_cases_1 | LGBM | agg | 0.6053 | 0.5308 | 30.0000 | 0.6053 | 0.6492 | [2, 4, 2, 3, 13] | {"learning_rate": 0.1323, "num_leaves": 17, "min_child_samples": 57, "subsample": 0.8353, "colsample_bytree": 0.4473, "reg_alpha": 0.0033, "reg_lambda": 0.0183} | 10.7683 |
| strict | sepsis_cases_1 | XGB | agg+index | 0.5953 | 0.6037 | 30.0000 | 0.6173 | 0.6728 | [6, 13, 8, 14, 4] | {"learning_rate": 0.0496, "max_depth": 3, "min_child_weight": 3.715, "subsample": 0.5904, "colsample_bytree": 0.9617, "gamma": 0.0038, "reg_alpha": 0.073, "reg_lambda": 0.0041} | 55.7993 |
| strict | traffic_fines_1 | CatBoost | agg+index | 0.7688 | 0.7717 | 20.0000 | 0.7717 | 0.7833 | [30, 34, 21, 15, 11] | {"learning_rate": 0.041, "depth": 4, "l2_leaf_reg": 11.2224, "bagging_temperature": 0.6022, "random_strength": 3.2554} | 55.3989 |
| strict | traffic_fines_1 | LGBM | agg+index | 0.7550 | 0.7649 | 30.0000 | 0.7649 | 0.7744 | [40, 1, 33, 35, 3] | {"learning_rate": 0.1715, "num_leaves": 15, "min_child_samples": 14, "subsample": 0.9869, "colsample_bytree": 0.3555, "reg_alpha": 0.0035, "reg_lambda": 0.0381} | 51.3466 |
| strict | traffic_fines_1 | XGB | agg | 0.7694 | 0.7649 | 30.0000 | 0.7692 | 0.7751 | [171, 4, 4, 14, 167] | {"learning_rate": 0.0947, "max_depth": 4, "min_child_weight": 5.3134, "subsample": 0.7297, "colsample_bytree": 0.575, "gamma": 0.0057, "reg_alpha": 1.7757, "reg_lambda": 0.016} | 231.7018 |


### Deep models: configuration search (validation AUC, seed 0) and epochs used per seed

| protocol | task | family | best_params | tuning | final_iters |
|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | LSTM | {"h": 64, "lr": 0.003} | [[{"h": 64, "lr": 0.001}, 0.6287], [{"h": 128, "lr": 0.001}, 0.6342], [{"h": 64, "lr": 0.003}, 0.6397]] | epochs [16, 16, 10, 10, 12] |
| benchmark | bpic2012_accepted | Transformer | {"d": 32, "layers": 1, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.6404], [{"d": 64, "layers": 2, "lr": 0.001}, 0.6398], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.6377]] | epochs [25, 25, 17, 21, 25] |
| benchmark | bpic2012_cancelled | LSTM | {"h": 64, "lr": 0.003} | [[{"h": 64, "lr": 0.001}, 0.6345], [{"h": 128, "lr": 0.001}, 0.6338], [{"h": 64, "lr": 0.003}, 0.6415]] | epochs [13, 17, 11, 9, 17] |
| benchmark | bpic2012_cancelled | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.6315], [{"d": 64, "layers": 2, "lr": 0.001}, 0.6336], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.6277]] | epochs [13, 14, 13, 12, 14] |
| benchmark | bpic2012_declined | LSTM | {"h": 64, "lr": 0.003} | [[{"h": 64, "lr": 0.001}, 0.5546], [{"h": 128, "lr": 0.001}, 0.5502], [{"h": 64, "lr": 0.003}, 0.5568]] | epochs [9, 12, 20, 13, 21] |
| benchmark | bpic2012_declined | Transformer | {"d": 32, "layers": 1, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.5667], [{"d": 64, "layers": 2, "lr": 0.001}, 0.5634], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.5507]] | epochs [18, 21, 24, 19, 16] |
| benchmark | bpic2017_accepted | LSTM | {"h": 64, "lr": 0.003} | [[{"h": 64, "lr": 0.001}, 0.8745], [{"h": 128, "lr": 0.001}, 0.8764], [{"h": 64, "lr": 0.003}, 0.8768]] | epochs [9, 7, 12, 9, 8] |
| benchmark | bpic2017_accepted | Transformer | {"d": 32, "layers": 1, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.8792], [{"d": 64, "layers": 2, "lr": 0.001}, 0.8789], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.8782]] | epochs [15, 17, 17, 20, 13] |
| benchmark | bpic2017_cancelled | LSTM | {"h": 64, "lr": 0.003} | [[{"h": 64, "lr": 0.001}, 0.7974], [{"h": 128, "lr": 0.001}, 0.7983], [{"h": 64, "lr": 0.003}, 0.7984]] | epochs [11, 11, 8, 7, 15] |
| benchmark | bpic2017_cancelled | Transformer | {"d": 32, "layers": 1, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.7999], [{"d": 64, "layers": 2, "lr": 0.001}, 0.7994], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.7992]] | epochs [22, 20, 25, 21, 23] |
| benchmark | bpic2017_refused | LSTM | {"h": 64, "lr": 0.001} | [[{"h": 64, "lr": 0.001}, 0.716], [{"h": 128, "lr": 0.001}, 0.7127], [{"h": 64, "lr": 0.003}, 0.7105]] | epochs [17, 18, 12, 16, 21] |
| benchmark | bpic2017_refused | Transformer | {"d": 32, "layers": 1, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.7142], [{"d": 64, "layers": 2, "lr": 0.001}, 0.7121], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.7112]] | epochs [16, 16, 13, 21, 15] |
| benchmark | sepsis_cases_1 | LSTM | {"h": 128, "lr": 0.001} | [[{"h": 64, "lr": 0.001}, 0.5067], [{"h": 128, "lr": 0.001}, 0.5736], [{"h": 64, "lr": 0.003}, 0.5713]] | epochs [19, 19, 19, 4, 21] |
| benchmark | sepsis_cases_1 | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.5037], [{"d": 64, "layers": 2, "lr": 0.001}, 0.6175], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.4954]] | epochs [16, 18, 14, 16, 15] |
| benchmark | sepsis_cases_2 | LSTM | {"h": 64, "lr": 0.003} | [[{"h": 64, "lr": 0.001}, 0.8674], [{"h": 128, "lr": 0.001}, 0.7146], [{"h": 64, "lr": 0.003}, 0.8703]] | epochs [19, 22, 20, 19, 22] |
| benchmark | sepsis_cases_2 | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.8625], [{"d": 64, "layers": 2, "lr": 0.001}, 0.8653], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.8323]] | epochs [18, 20, 19, 19, 23] |
| benchmark | sepsis_cases_3 | LSTM | {"h": 128, "lr": 0.001} | [[{"h": 64, "lr": 0.001}, 0.6965], [{"h": 128, "lr": 0.001}, 0.7235], [{"h": 64, "lr": 0.003}, 0.7152]] | epochs [24, 22, 24, 24, 19] |
| benchmark | sepsis_cases_3 | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.6703], [{"d": 64, "layers": 2, "lr": 0.001}, 0.7556], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.6992]] | epochs [24, 14, 25, 21, 25] |
| benchmark | traffic_fines_1 | LSTM | {"h": 64, "lr": 0.003} | [[{"h": 64, "lr": 0.001}, 0.7921], [{"h": 128, "lr": 0.001}, 0.792], [{"h": 64, "lr": 0.003}, 0.793]] | epochs [4, 5, 9, 4, 7] |
| benchmark | traffic_fines_1 | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.7923], [{"d": 64, "layers": 2, "lr": 0.001}, 0.7924], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.792]] | epochs [7, 8, 6, 8, 11] |
| strict | bpic2012_accepted | LSTM | {"h": 128, "lr": 0.001} | [[{"h": 64, "lr": 0.001}, 0.546], [{"h": 128, "lr": 0.001}, 0.5517], [{"h": 64, "lr": 0.003}, 0.5484]] | epochs [11, 8, 11, 9, 13] |
| strict | bpic2012_accepted | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.5602], [{"d": 64, "layers": 2, "lr": 0.001}, 0.5621], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.5607]] | epochs [16, 20, 11, 9, 14] |
| strict | bpic2017_accepted | LSTM | {"h": 64, "lr": 0.003} | [[{"h": 64, "lr": 0.001}, 0.6445], [{"h": 128, "lr": 0.001}, 0.6506], [{"h": 64, "lr": 0.003}, 0.6527]] | epochs [11, 14, 12, 10, 10] |
| strict | bpic2017_accepted | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.6508], [{"d": 64, "layers": 2, "lr": 0.001}, 0.6567], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.653]] | epochs [15, 11, 15, 16, 17] |
| strict | sepsis_cases_1 | LSTM | {"h": 128, "lr": 0.001} | [[{"h": 64, "lr": 0.001}, 0.4941], [{"h": 128, "lr": 0.001}, 0.5799], [{"h": 64, "lr": 0.003}, 0.5795]] | epochs [17, 19, 21, 19, 18] |
| strict | sepsis_cases_1 | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.5861], [{"d": 64, "layers": 2, "lr": 0.001}, 0.5921], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.4692]] | epochs [16, 14, 18, 15, 16] |
| strict | traffic_fines_1 | LSTM | {"h": 128, "lr": 0.001} | [[{"h": 64, "lr": 0.001}, 0.7821], [{"h": 128, "lr": 0.001}, 0.783], [{"h": 64, "lr": 0.003}, 0.7818]] | epochs [4, 5, 5, 7, 4] |
| strict | traffic_fines_1 | Transformer | {"d": 64, "layers": 2, "lr": 0.001} | [[{"d": 32, "layers": 1, "lr": 0.001}, 0.7818], [{"d": 64, "layers": 2, "lr": 0.001}, 0.7831], [{"d": 64, "layers": 2, "lr": 0.0003}, 0.7827]] | epochs [8, 6, 5, 7, 5] |


LR regularisation chosen: benchmark/bpic2012_accepted: C=0.01; benchmark/bpic2012_cancelled: C=1.0; benchmark/bpic2012_declined: C=0.01; benchmark/bpic2017_accepted: C=0.01; benchmark/bpic2017_cancelled: C=0.01; benchmark/bpic2017_refused: C=0.01; benchmark/sepsis_cases_1: C=1.0; benchmark/sepsis_cases_2: C=0.01; benchmark/sepsis_cases_3: C=1.0; benchmark/traffic_fines_1: C=0.01; strict/bpic2012_accepted: C=0.01; strict/bpic2017_accepted: C=0.01; strict/sepsis_cases_1: C=1.0; strict/traffic_fines_1: C=0.01

## 4. Predictive performance (test set, all prefixes pooled)

### BENCHMARK: AUC mean ± sd over seeds

| task | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | 0.6469 | 0.6905 ± 0.0038 | 0.6982 ± 0.0096 | 0.6975 ± 0.0030 | 0.7000 ± 0.0029 | 0.6931 ± 0.0022 | 0.6823 ± 0.0061 | 0.7047 ± 0.0040 |
| bpic2012_cancelled | 0.7052 | 0.7364 ± 0.0031 | 0.7178 ± 0.0068 | 0.7260 ± 0.0046 | 0.7243 ± 0.0099 | 0.7258 ± 0.0033 | 0.7143 ± 0.0033 | 0.7275 ± 0.0020 |
| bpic2012_declined | 0.5478 | 0.5646 ± 0.0019 | 0.5984 ± 0.0076 | 0.5703 ± 0.0124 | 0.5897 ± 0.0114 | 0.5890 ± 0.0123 | 0.5740 ± 0.0148 | 0.5878 ± 0.0168 |
| bpic2017_accepted | 0.7099 | 0.8945 ± 0.0004 | 0.8990 ± 0.0001 | 0.8990 ± 0.0005 | 0.8982 ± 0.0004 | 0.8800 ± 0.0028 | 0.8813 ± 0.0017 | 0.8993 ± 0.0003 |
| bpic2017_cancelled | 0.6403 | 0.8586 ± 0.0004 | 0.8620 ± 0.0014 | 0.8636 ± 0.0007 | 0.8623 ± 0.0010 | 0.7892 ± 0.0036 | 0.7916 ± 0.0019 | 0.8638 ± 0.0006 |
| bpic2017_refused | 0.6468 | 0.8423 ± 0.0012 | 0.8516 ± 0.0036 | 0.8550 ± 0.0015 | 0.8497 ± 0.0034 | 0.7320 ± 0.0052 | 0.7377 ± 0.0025 | 0.8531 ± 0.0021 |
| sepsis_cases_1 | 0.5037 | 0.3672 ± 0.0154 | 0.4154 ± 0.0342 | 0.3632 ± 0.0469 | 0.4747 ± 0.0109 | 0.4055 ± 0.0355 | 0.3960 ± 0.0218 | 0.4173 ± 0.0234 |
| sepsis_cases_2 | 0.8855 | 0.8453 ± 0.0064 | 0.8548 ± 0.0118 | 0.8296 ± 0.0141 | 0.8223 ± 0.0301 | 0.8236 ± 0.0094 | 0.8372 ± 0.0047 | 0.8301 ± 0.0310 |
| sepsis_cases_3 | 0.7038 | 0.6962 ± 0.0082 | 0.6655 ± 0.0223 | 0.6401 ± 0.0266 | 0.6756 ± 0.0131 | 0.6658 ± 0.0169 | 0.6977 ± 0.0333 | 0.7162 ± 0.0060 |
| traffic_fines_1 | 0.7935 | 0.7818 ± 0.0014 | 0.7779 ± 0.0024 | 0.7843 ± 0.0041 | 0.7883 ± 0.0041 | 0.7926 ± 0.0020 | 0.7928 ± 0.0018 | 0.7932 ± 0.0025 |


BENCHMARK: seed-0 AUC with 95% case-cluster bootstrap CI (1,000 resamples of test cases)

| task | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | 0.6469 [0.6265, 0.6676] | 0.6883 [0.6701, 0.7072] | 0.6971 [0.6757, 0.7197] | 0.6926 [0.6721, 0.7127] | 0.6966 [0.6766, 0.7166] | 0.6909 [0.6723, 0.7099] | 0.6875 [0.6680, 0.7061] | 0.7008 [0.6807, 0.7212] |
| bpic2012_cancelled | 0.7052 [0.6827, 0.7272] | 0.7338 [0.7145, 0.7542] | 0.7135 [0.6939, 0.7336] | 0.7234 [0.7010, 0.7456] | 0.7262 [0.7019, 0.7517] | 0.7246 [0.7038, 0.7459] | 0.7163 [0.6952, 0.7386] | 0.7245 [0.7037, 0.7463] |
| bpic2012_declined | 0.5478 [0.5108, 0.5829] | 0.5671 [0.5337, 0.6017] | 0.6078 [0.5689, 0.6441] | 0.5757 [0.5367, 0.6109] | 0.5817 [0.5443, 0.6196] | 0.5846 [0.5675, 0.6010] | 0.5858 [0.5559, 0.6115] | 0.5904 [0.5516, 0.6250] |
| bpic2017_accepted | 0.7099 [0.7000, 0.7203] | 0.8940 [0.8894, 0.8989] | 0.8989 [0.8943, 0.9036] | 0.8994 [0.8949, 0.9042] | 0.8987 [0.8943, 0.9034] | 0.8752 [0.8703, 0.8802] | 0.8797 [0.8745, 0.8850] | 0.8996 [0.8950, 0.9042] |
| bpic2017_cancelled | 0.6403 [0.6303, 0.6499] | 0.8578 [0.8526, 0.8635] | 0.8639 [0.8586, 0.8692] | 0.8642 [0.8592, 0.8697] | 0.8628 [0.8574, 0.8684] | 0.7917 [0.7848, 0.7993] | 0.7938 [0.7868, 0.8012] | 0.8645 [0.8593, 0.8699] |
| bpic2017_refused | 0.6468 [0.6307, 0.6650] | 0.8425 [0.8342, 0.8513] | 0.8466 [0.8382, 0.8555] | 0.8545 [0.8459, 0.8636] | 0.8532 [0.8439, 0.8629] | 0.7298 [0.7201, 0.7403] | 0.7392 [0.7293, 0.7488] | 0.8552 [0.8462, 0.8644] |
| sepsis_cases_1 | 0.5037 [0.3736, 0.6440] | 0.3482 [0.2323, 0.4837] | 0.3637 [0.2469, 0.4829] | 0.4252 [0.2984, 0.5512] | 0.4687 [0.2958, 0.6265] | 0.3907 [0.2744, 0.5141] | 0.3625 [0.2514, 0.4867] | 0.3770 [0.2290, 0.5167] |
| sepsis_cases_2 | 0.8855 [0.8145, 0.9453] | 0.8459 [0.7396, 0.9390] | 0.8568 [0.7463, 0.9524] | 0.8410 [0.7169, 0.9436] | 0.8246 [0.7153, 0.9196] | 0.8225 [0.7328, 0.9049] | 0.8303 [0.7490, 0.9122] | 0.8185 [0.7039, 0.9140] |
| sepsis_cases_3 | 0.7038 [0.6025, 0.8005] | 0.6975 [0.5878, 0.8031] | 0.6667 [0.5610, 0.7662] | 0.6828 [0.5599, 0.8022] | 0.6789 [0.5402, 0.8068] | 0.6912 [0.5984, 0.7796] | 0.7061 [0.5984, 0.8068] | 0.7253 [0.6228, 0.8295] |
| traffic_fines_1 | 0.7935 [0.7901, 0.7970] | 0.7833 [0.7802, 0.7867] | 0.7742 [0.7710, 0.7777] | 0.7809 [0.7777, 0.7841] | 0.7940 [0.7908, 0.7973] | 0.7911 [0.7881, 0.7943] | 0.7952 [0.7921, 0.7983] | 0.7953 [0.7923, 0.7982] |


BENCHMARK: BRIER mean ± sd

| task | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | 0.2388 | 0.2214 ± 0.0005 | 0.2181 ± 0.0051 | 0.2166 ± 0.0017 | 0.2141 ± 0.0003 | 0.2156 ± 0.0028 | 0.2206 ± 0.0019 | 0.2115 ± 0.0011 |
| bpic2012_cancelled | 0.1670 | 0.1707 ± 0.0011 | 0.1706 ± 0.0045 | 0.1700 ± 0.0053 | 0.1857 ± 0.0161 | 0.1648 ± 0.0031 | 0.1661 ± 0.0020 | 0.1603 ± 0.0011 |
| bpic2012_declined | 0.1582 | 0.1560 ± 0.0008 | 0.1447 ± 0.0007 | 0.1488 ± 0.0017 | 0.1491 ± 0.0043 | 0.1461 ± 0.0020 | 0.1485 ± 0.0028 | 0.1458 ± 0.0014 |
| bpic2017_accepted | 0.2272 | 0.1230 ± 0.0002 | 0.1214 ± 0.0019 | 0.1206 ± 0.0013 | 0.1202 ± 0.0001 | 0.1303 ± 0.0012 | 0.1306 ± 0.0015 | 0.1195 ± 0.0001 |
| bpic2017_cancelled | 0.3033 | 0.1494 ± 0.0001 | 0.1469 ± 0.0014 | 0.1494 ± 0.0045 | 0.1455 ± 0.0002 | 0.1824 ± 0.0015 | 0.1815 ± 0.0008 | 0.1446 ± 0.0001 |
| bpic2017_refused | 0.1045 | 0.0774 ± 0.0002 | 0.0928 ± 0.0095 | 0.0956 ± 0.0056 | 0.0833 ± 0.0137 | 0.1033 ± 0.0005 | 0.1025 ± 0.0003 | 0.0739 ± 0.0001 |
| sepsis_cases_1 | 0.1152 | 0.1160 ± 0.0011 | 0.1050 ± 0.0021 | 0.1010 ± 0.0012 | 0.1445 ± 0.0287 | 0.1199 ± 0.0291 | 0.1123 ± 0.0031 | 0.1259 ± 0.0198 |
| sepsis_cases_2 | 0.0562 | 0.0625 ± 0.0004 | 0.0685 ± 0.0052 | 0.0679 ± 0.0072 | 0.0618 ± 0.0031 | 0.0740 ± 0.0022 | 0.0697 ± 0.0035 | 0.0873 ± 0.0243 |
| sepsis_cases_3 | 0.1474 | 0.1375 ± 0.0013 | 0.1451 ± 0.0037 | 0.1436 ± 0.0036 | 0.1452 ± 0.0070 | 0.1478 ± 0.0024 | 0.1440 ± 0.0056 | 0.1383 ± 0.0022 |
| traffic_fines_1 | 0.1791 | 0.1842 ± 0.0007 | 0.1825 ± 0.0013 | 0.1898 ± 0.0143 | 0.1817 ± 0.0008 | 0.1800 ± 0.0016 | 0.1825 ± 0.0019 | 0.1842 ± 0.0016 |


BENCHMARK: ECE mean ± sd

| task | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | 0.0955 | 0.0726 ± 0.0016 | 0.0757 ± 0.0209 | 0.0669 ± 0.0075 | 0.0468 ± 0.0045 | 0.0560 ± 0.0149 | 0.0528 ± 0.0079 | 0.0459 ± 0.0019 |
| bpic2012_cancelled | 0.0369 | 0.1105 ± 0.0058 | 0.0868 ± 0.0189 | 0.0978 ± 0.0139 | 0.1515 ± 0.0558 | 0.0745 ± 0.0117 | 0.0516 ± 0.0146 | 0.0481 ± 0.0035 |
| bpic2012_declined | 0.0842 | 0.0847 ± 0.0028 | 0.0260 ± 0.0057 | 0.0466 ± 0.0052 | 0.0611 ± 0.0352 | 0.0354 ± 0.0156 | 0.0269 ± 0.0066 | 0.0394 ± 0.0051 |
| bpic2017_accepted | 0.1516 | 0.0168 ± 0.0006 | 0.0339 ± 0.0190 | 0.0303 ± 0.0133 | 0.0201 ± 0.0036 | 0.0188 ± 0.0058 | 0.0250 ± 0.0089 | 0.0134 ± 0.0008 |
| bpic2017_cancelled | 0.2128 | 0.0320 ± 0.0011 | 0.0295 ± 0.0108 | 0.0533 ± 0.0273 | 0.0290 ± 0.0024 | 0.0312 ± 0.0067 | 0.0312 ± 0.0096 | 0.0130 ± 0.0022 |
| bpic2017_refused | 0.0592 | 0.0201 ± 0.0013 | 0.0574 ± 0.0114 | 0.0627 ± 0.0053 | 0.0695 ± 0.0632 | 0.0187 ± 0.0064 | 0.0135 ± 0.0028 | 0.0174 ± 0.0012 |
| sepsis_cases_1 | 0.0968 | 0.1218 ± 0.0068 | 0.0716 ± 0.0172 | 0.0575 ± 0.0148 | 0.2013 ± 0.0755 | 0.1223 ± 0.0842 | 0.0905 ± 0.0121 | 0.1357 ± 0.0390 |
| sepsis_cases_2 | 0.0348 | 0.0491 ± 0.0022 | 0.0812 ± 0.0156 | 0.0633 ± 0.0160 | 0.0447 ± 0.0087 | 0.0405 ± 0.0064 | 0.0329 ± 0.0081 | 0.0843 ± 0.0368 |
| sepsis_cases_3 | 0.0802 | 0.0460 ± 0.0095 | 0.0416 ± 0.0074 | 0.0506 ± 0.0053 | 0.0931 ± 0.0183 | 0.0514 ± 0.0075 | 0.0738 ± 0.0203 | 0.0627 ± 0.0083 |
| traffic_fines_1 | 0.0520 | 0.0513 ± 0.0032 | 0.0647 ± 0.0073 | 0.0797 ± 0.0178 | 0.0654 ± 0.0080 | 0.0482 ± 0.0132 | 0.0661 ± 0.0159 | 0.0679 ± 0.0048 |


BENCHMARK: log-loss, accuracy, macro-F1 (threshold 0.5), training time (s, per seed; Stack = sum of its 4 base models) and inference time (ms per 1,000 prefixes)

| task | model | logloss_mean | acc_mean | f1_macro_mean | train_s_mean | infer_ms_per_1000_mean |
|---|---|---|---|---|---|---|
| bpic2012_accepted | CatBoost | 0.612 | 0.615 | 0.613 | 8.762 | 3.134 |
| bpic2012_accepted | LGBM | 0.616 | 0.616 | 0.613 | 3.165 | 1.201 |
| bpic2012_accepted | LR | 0.758 | 0.592 | 0.590 | 1.123 | 0.430 |
| bpic2012_accepted | LSTM | 0.611 | 0.617 | 0.615 | 7.039 | 1.423 |
| bpic2012_accepted | RF | 0.628 | 0.622 | 0.622 | 35.308 | 17.209 |
| bpic2012_accepted | Stack (proposed) | 0.602 | 0.625 | 0.625 | 36.852 | 8.200 |
| bpic2012_accepted | Transformer | 0.626 | 0.610 | 0.608 | 23.096 | 3.248 |
| bpic2012_accepted | XGB | 0.618 | 0.607 | 0.601 | 1.829 | 0.618 |
| bpic2012_cancelled | CatBoost | 0.553 | 0.776 | 0.591 | 5.425 | 2.377 |
| bpic2012_cancelled | LGBM | 0.515 | 0.774 | 0.570 | 3.449 | 1.779 |
| bpic2012_cancelled | LR | 0.527 | 0.766 | 0.537 | 1.779 | 0.801 |
| bpic2012_cancelled | LSTM | 0.494 | 0.771 | 0.599 | 7.387 | 1.997 |
| bpic2012_cancelled | RF | 0.513 | 0.749 | 0.620 | 48.080 | 22.199 |
| bpic2012_cancelled | Stack (proposed) | 0.484 | 0.778 | 0.592 | 53.078 | 13.140 |
| bpic2012_cancelled | Transformer | 0.498 | 0.769 | 0.575 | 40.887 | 8.128 |
| bpic2012_cancelled | XGB | 0.514 | 0.766 | 0.576 | 3.317 | 0.857 |
| bpic2012_declined | CatBoost | 0.474 | 0.823 | 0.518 | 5.834 | 2.137 |
| bpic2012_declined | LGBM | 0.472 | 0.819 | 0.520 | 2.253 | 1.513 |
| bpic2012_declined | LR | 0.688 | 0.818 | 0.505 | 0.809 | 0.472 |
| bpic2012_declined | LSTM | 0.464 | 0.822 | 0.514 | 12.957 | 2.678 |
| bpic2012_declined | RF | 0.490 | 0.821 | 0.518 | 43.027 | 16.259 |
| bpic2012_declined | Stack (proposed) | 0.464 | 0.823 | 0.519 | 42.267 | 8.885 |
| bpic2012_declined | Transformer | 0.472 | 0.817 | 0.489 | 22.115 | 4.038 |
| bpic2012_declined | XGB | 0.462 | 0.823 | 0.518 | 12.065 | 1.197 |
| bpic2017_accepted | CatBoost | 0.371 | 0.820 | 0.799 | 6.556 | 4.260 |
| bpic2017_accepted | LGBM | 0.377 | 0.820 | 0.799 | 3.611 | 1.374 |
| bpic2017_accepted | LR | 1.326 | 0.716 | 0.648 | 1.504 | 1.630 |
| bpic2017_accepted | LSTM | 0.394 | 0.801 | 0.778 | 4.710 | 1.653 |
| bpic2017_accepted | RF | 0.380 | 0.815 | 0.796 | 27.630 | 31.846 |
| bpic2017_accepted | Stack (proposed) | 0.367 | 0.820 | 0.799 | 33.221 | 9.784 |
| bpic2017_accepted | Transformer | 0.395 | 0.803 | 0.779 | 15.908 | 2.702 |
| bpic2017_accepted | XGB | 0.380 | 0.820 | 0.799 | 7.145 | 1.448 |
| bpic2017_cancelled | CatBoost | 0.443 | 0.753 | 0.752 | 7.278 | 4.247 |
| bpic2017_cancelled | LGBM | 0.460 | 0.755 | 0.755 | 5.224 | 3.468 |
| bpic2017_cancelled | LR | 2.095 | 0.607 | 0.592 | 1.865 | 1.516 |
| bpic2017_cancelled | LSTM | 0.533 | 0.693 | 0.690 | 6.493 | 1.935 |
| bpic2017_cancelled | RF | 0.451 | 0.750 | 0.750 | 20.217 | 20.870 |
| bpic2017_cancelled | Stack (proposed) | 0.439 | 0.755 | 0.755 | 87.686 | 12.201 |
| bpic2017_cancelled | Transformer | 0.531 | 0.695 | 0.692 | 24.494 | 2.752 |
| bpic2017_cancelled | XGB | 0.446 | 0.754 | 0.754 | 50.689 | 1.734 |
| bpic2017_refused | CatBoost | 0.290 | 0.913 | 0.750 | 14.009 | 5.274 |
| bpic2017_refused | LGBM | 0.325 | 0.872 | 0.466 | 3.440 | 1.712 |
| bpic2017_refused | LR | 0.662 | 0.884 | 0.584 | 2.097 | 1.635 |
| bpic2017_refused | LSTM | 0.336 | 0.872 | 0.476 | 12.657 | 2.532 |
| bpic2017_refused | RF | 0.267 | 0.909 | 0.730 | 31.191 | 34.694 |
| bpic2017_refused | Stack (proposed) | 0.257 | 0.915 | 0.755 | 86.012 | 11.337 |
| bpic2017_refused | Transformer | 0.335 | 0.873 | 0.496 | 17.177 | 2.802 |
| bpic2017_refused | XGB | 0.318 | 0.873 | 0.470 | 51.385 | 1.549 |
| sepsis_cases_1 | CatBoost | 0.470 | 0.881 | 0.468 | 1.785 | 6.462 |
| sepsis_cases_1 | LGBM | 0.360 | 0.891 | 0.471 | 0.627 | 3.659 |
| sepsis_cases_1 | LR | 0.440 | 0.874 | 0.476 | 0.351 | 0.666 |
| sepsis_cases_1 | LSTM | 0.415 | 0.891 | 0.471 | 3.630 | 6.710 |
| sepsis_cases_1 | RF | 0.409 | 0.889 | 0.498 | 3.442 | 29.129 |
| sepsis_cases_1 | Stack (proposed) | 0.424 | 0.863 | 0.479 | 9.115 | 20.918 |
| sepsis_cases_1 | Transformer | 0.395 | 0.890 | 0.500 | 5.958 | 8.110 |
| sepsis_cases_1 | XGB | 0.373 | 0.891 | 0.471 | 0.745 | 2.687 |
| sepsis_cases_2 | CatBoost | 0.246 | 0.928 | 0.761 | 2.032 | 10.304 |
| sepsis_cases_2 | LGBM | 0.250 | 0.919 | 0.634 | 0.630 | 3.792 |
| sepsis_cases_2 | LR | 0.202 | 0.935 | 0.782 | 0.077 | 1.042 |
| sepsis_cases_2 | LSTM | 0.261 | 0.904 | 0.535 | 0.994 | 3.485 |
| sepsis_cases_2 | RF | 0.234 | 0.931 | 0.733 | 2.043 | 27.652 |
| sepsis_cases_2 | Stack (proposed) | 0.327 | 0.887 | 0.722 | 11.304 | 26.676 |
| sepsis_cases_2 | Transformer | 0.249 | 0.913 | 0.698 | 4.929 | 9.122 |
| sepsis_cases_2 | XGB | 0.249 | 0.903 | 0.524 | 3.713 | 3.458 |
| sepsis_cases_3 | CatBoost | 0.539 | 0.820 | 0.612 | 1.718 | 9.556 |
| sepsis_cases_3 | LGBM | 0.464 | 0.814 | 0.530 | 0.687 | 1.714 |
| sepsis_cases_3 | LR | 0.535 | 0.806 | 0.608 | 0.400 | 0.935 |
| sepsis_cases_3 | LSTM | 0.468 | 0.813 | 0.450 | 4.159 | 7.773 |
| sepsis_cases_3 | RF | 0.441 | 0.812 | 0.529 | 2.937 | 37.681 |
| sepsis_cases_3 | Stack (proposed) | 0.447 | 0.822 | 0.650 | 11.626 | 24.729 |
| sepsis_cases_3 | Transformer | 0.465 | 0.820 | 0.495 | 6.354 | 10.813 |
| sepsis_cases_3 | XGB | 0.464 | 0.810 | 0.461 | 2.867 | 2.645 |
| traffic_fines_1 | CatBoost | 0.528 | 0.688 | 0.673 | 5.621 | 3.654 |
| traffic_fines_1 | LGBM | 0.551 | 0.695 | 0.687 | 4.283 | 2.043 |
| traffic_fines_1 | LR | 0.523 | 0.724 | 0.723 | 0.914 | 0.676 |
| traffic_fines_1 | LSTM | 0.524 | 0.723 | 0.722 | 12.010 | 4.807 |
| traffic_fines_1 | RF | 0.534 | 0.708 | 0.707 | 16.112 | 23.556 |
| traffic_fines_1 | Stack (proposed) | 0.531 | 0.690 | 0.676 | 74.322 | 19.055 |
| traffic_fines_1 | Transformer | 0.531 | 0.714 | 0.711 | 54.556 | 11.132 |
| traffic_fines_1 | XGB | 0.531 | 0.702 | 0.700 | 9.862 | 2.226 |

### STRICT: AUC mean ± sd over seeds

| task | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | 0.5273 | 0.5677 ± 0.0022 | 0.5669 ± 0.0123 | 0.5694 ± 0.0055 | 0.5774 ± 0.0061 | 0.5539 ± 0.0126 | 0.5649 ± 0.0038 | 0.5710 ± 0.0117 |
| bpic2017_accepted | 0.5538 | 0.6690 ± 0.0005 | 0.6794 ± 0.0006 | 0.6805 ± 0.0012 | 0.6769 ± 0.0006 | 0.6551 ± 0.0025 | 0.6621 ± 0.0018 | 0.6810 ± 0.0007 |
| sepsis_cases_1 | 0.5280 | 0.4082 ± 0.0193 | 0.4109 ± 0.0246 | 0.3905 ± 0.0435 | 0.5110 ± 0.0474 | 0.4040 ± 0.0054 | 0.4122 ± 0.0127 | 0.4919 ± 0.0332 |
| traffic_fines_1 | 0.7083 | 0.7642 ± 0.0015 | 0.7773 ± 0.0028 | 0.7769 ± 0.0089 | 0.7843 ± 0.0048 | 0.7896 ± 0.0023 | 0.7908 ± 0.0012 | 0.7914 ± 0.0012 |


STRICT: seed-0 AUC with 95% case-cluster bootstrap CI (1,000 resamples of test cases)

| task | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | 0.5273 [0.4989, 0.5551] | 0.5710 [0.5449, 0.5995] | 0.5486 [0.5191, 0.5789] | 0.5740 [0.5471, 0.6016] | 0.5744 [0.5490, 0.6010] | 0.5523 [0.5263, 0.5763] | 0.5643 [0.5376, 0.5891] | 0.5518 [0.5225, 0.5818] |
| bpic2017_accepted | 0.5538 [0.5423, 0.5652] | 0.6694 [0.6592, 0.6803] | 0.6805 [0.6694, 0.6915] | 0.6803 [0.6692, 0.6910] | 0.6772 [0.6662, 0.6875] | 0.6555 [0.6450, 0.6663] | 0.6648 [0.6540, 0.6759] | 0.6808 [0.6697, 0.6918] |
| sepsis_cases_1 | 0.5280 [0.3919, 0.6709] | 0.4162 [0.2987, 0.5327] | 0.3918 [0.2718, 0.5111] | 0.3756 [0.2538, 0.5143] | 0.5455 [0.4228, 0.6829] | 0.4096 [0.2991, 0.5192] | 0.4061 [0.2965, 0.5310] | 0.5078 [0.3912, 0.6451] |
| traffic_fines_1 | 0.7083 [0.7035, 0.7137] | 0.7625 [0.7594, 0.7654] | 0.7744 [0.7710, 0.7776] | 0.7768 [0.7734, 0.7798] | 0.7857 [0.7825, 0.7885] | 0.7905 [0.7876, 0.7934] | 0.7911 [0.7884, 0.7939] | 0.7927 [0.7898, 0.7956] |


STRICT: BRIER mean ± sd

| task | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | 0.2601 | 0.2500 ± 0.0005 | 0.2531 ± 0.0061 | 0.2468 ± 0.0017 | 0.2451 ± 0.0006 | 0.2500 ± 0.0029 | 0.2540 ± 0.0072 | 0.2472 ± 0.0030 |
| bpic2017_accepted | 0.2938 | 0.2202 ± 0.0002 | 0.2166 ± 0.0004 | 0.2170 ± 0.0012 | 0.2177 ± 0.0005 | 0.2226 ± 0.0013 | 0.2215 ± 0.0005 | 0.2159 ± 0.0001 |
| sepsis_cases_1 | 0.1098 | 0.1120 ± 0.0010 | 0.1010 ± 0.0012 | 0.1041 ± 0.0028 | 0.1142 ± 0.0108 | 0.1054 ± 0.0012 | 0.1073 ± 0.0024 | 0.1169 ± 0.0138 |
| traffic_fines_1 | 0.2705 | 0.1956 ± 0.0010 | 0.2073 ± 0.0104 | 0.2059 ± 0.0135 | 0.1939 ± 0.0049 | 0.1881 ± 0.0043 | 0.1900 ± 0.0068 | 0.1860 ± 0.0030 |


STRICT: ECE mean ± sd

| task | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | 0.0718 | 0.0581 ± 0.0026 | 0.0741 ± 0.0241 | 0.0499 ± 0.0052 | 0.0380 ± 0.0019 | 0.0632 ± 0.0224 | 0.0892 ± 0.0359 | 0.0483 ± 0.0107 |
| bpic2017_accepted | 0.1750 | 0.0353 ± 0.0014 | 0.0217 ± 0.0044 | 0.0263 ± 0.0063 | 0.0287 ± 0.0063 | 0.0337 ± 0.0089 | 0.0351 ± 0.0037 | 0.0155 ± 0.0011 |
| sepsis_cases_1 | 0.0884 | 0.1103 ± 0.0153 | 0.0656 ± 0.0168 | 0.0826 ± 0.0139 | 0.1008 ± 0.0418 | 0.0772 ± 0.0063 | 0.0781 ± 0.0089 | 0.1092 ± 0.0198 |
| traffic_fines_1 | 0.2149 | 0.0802 ± 0.0025 | 0.1267 ± 0.0285 | 0.1155 ± 0.0270 | 0.0809 ± 0.0269 | 0.0652 ± 0.0333 | 0.0776 ± 0.0375 | 0.0541 ± 0.0209 |


STRICT: log-loss, accuracy, macro-F1 (threshold 0.5), training time (s, per seed; Stack = sum of its 4 base models) and inference time (ms per 1,000 prefixes)

| task | model | logloss_mean | acc_mean | f1_macro_mean | train_s_mean | infer_ms_per_1000_mean |
|---|---|---|---|---|---|---|
| bpic2012_accepted | CatBoost | 0.683 | 0.530 | 0.466 | 3.782 | 2.896 |
| bpic2012_accepted | LGBM | 0.687 | 0.533 | 0.525 | 3.070 | 2.291 |
| bpic2012_accepted | LR | 0.735 | 0.510 | 0.508 | 0.471 | 0.757 |
| bpic2012_accepted | LSTM | 0.693 | 0.525 | 0.484 | 7.569 | 4.007 |
| bpic2012_accepted | RF | 0.694 | 0.540 | 0.535 | 20.027 | 22.038 |
| bpic2012_accepted | Stack (proposed) | 0.688 | 0.541 | 0.540 | 24.419 | 10.206 |
| bpic2012_accepted | Transformer | 0.702 | 0.522 | 0.465 | 14.961 | 3.413 |
| bpic2012_accepted | XGB | 0.703 | 0.541 | 0.541 | 2.606 | 1.605 |
| bpic2017_accepted | CatBoost | 0.622 | 0.644 | 0.607 | 4.931 | 1.493 |
| bpic2017_accepted | LGBM | 0.620 | 0.648 | 0.607 | 4.064 | 2.422 |
| bpic2017_accepted | LR | 1.730 | 0.610 | 0.518 | 0.948 | 0.891 |
| bpic2017_accepted | LSTM | 0.632 | 0.630 | 0.590 | 5.503 | 1.485 |
| bpic2017_accepted | RF | 0.627 | 0.638 | 0.609 | 19.406 | 24.432 |
| bpic2017_accepted | Stack (proposed) | 0.617 | 0.650 | 0.607 | 96.233 | 10.155 |
| bpic2017_accepted | Transformer | 0.630 | 0.634 | 0.596 | 30.364 | 4.287 |
| bpic2017_accepted | XGB | 0.619 | 0.649 | 0.606 | 56.873 | 1.953 |
| sepsis_cases_1 | CatBoost | 0.410 | 0.881 | 0.481 | 1.867 | 4.412 |
| sepsis_cases_1 | LGBM | 0.369 | 0.890 | 0.471 | 0.365 | 1.247 |
| sepsis_cases_1 | LR | 0.421 | 0.879 | 0.478 | 0.200 | 1.032 |
| sepsis_cases_1 | LSTM | 0.379 | 0.891 | 0.471 | 2.104 | 4.588 |
| sepsis_cases_1 | RF | 0.394 | 0.889 | 0.504 | 2.011 | 26.026 |
| sepsis_cases_1 | Stack (proposed) | 0.399 | 0.869 | 0.481 | 6.934 | 13.072 |
| sepsis_cases_1 | Transformer | 0.381 | 0.891 | 0.471 | 2.834 | 5.177 |
| sepsis_cases_1 | XGB | 0.360 | 0.891 | 0.471 | 1.869 | 2.237 |
| traffic_fines_1 | CatBoost | 0.562 | 0.716 | 0.714 | 5.509 | 3.912 |
| traffic_fines_1 | LGBM | 0.589 | 0.703 | 0.701 | 3.185 | 1.500 |
| traffic_fines_1 | LR | 0.937 | 0.629 | 0.624 | 1.003 | 1.315 |
| traffic_fines_1 | LSTM | 0.544 | 0.709 | 0.706 | 19.343 | 11.299 |
| traffic_fines_1 | RF | 0.561 | 0.708 | 0.708 | 13.964 | 26.199 |
| traffic_fines_1 | Stack (proposed) | 0.536 | 0.713 | 0.712 | 69.478 | 20.508 |
| traffic_fines_1 | Transformer | 0.549 | 0.699 | 0.696 | 50.446 | 12.645 |
| traffic_fines_1 | XGB | 0.595 | 0.681 | 0.677 | 10.337 | 2.451 |

## 5. Statistical comparison

Friedman test over tasks on the seed-averaged test AUC of the 8 main models; Iman–Davenport F; Nemenyi critical difference (α = 0.05, q from the studentised range / √2). Wilcoxon signed-rank (two-sided) of the proposed model against each baseline across tasks, Holm-corrected over the 7 comparisons. With 4 STRICT tasks the smallest attainable two-sided Wilcoxon p is 0.125, so STRICT tests cannot reach significance by construction.

| protocol | n_tasks | k_models | friedman_chi2 | friedman_p | iman_davenport_F | nemenyi_q_alpha | nemenyi_CD |
|---|---|---|---|---|---|---|---|
| benchmark | 10 | 8 | 13.7333 | 0.0561 | 2.1967 | 3.0309 | 3.3202 |
| strict | 4 | 8 | 11.3333 | 0.1247 | 2.0400 | 3.0309 | 5.2496 |


Average ranks (1 = best) and wins

| protocol | model | avg_rank | wins | n_tasks | mean_auc |
|---|---|---|---|---|---|
| benchmark | Stack (proposed) | 2.2000 | 4 | 10 | 0.7393 |
| benchmark | CatBoost | 4.0000 | 0 | 10 | 0.7385 |
| benchmark | XGB | 4.1000 | 1 | 10 | 0.7341 |
| benchmark | LGBM | 4.6000 | 1 | 10 | 0.7229 |
| benchmark | RF | 5.0000 | 1 | 10 | 0.7277 |
| benchmark | LR | 5.3000 | 3 | 10 | 0.6783 |
| benchmark | Transformer | 5.3000 | 0 | 10 | 0.7105 |
| benchmark | LSTM | 5.5000 | 0 | 10 | 0.7097 |
| strict | Stack (proposed) | 1.7500 | 2 | 4 | 0.6338 |
| strict | CatBoost | 2.7500 | 1 | 4 | 0.6374 |
| strict | XGB | 4.5000 | 0 | 4 | 0.6086 |
| strict | Transformer | 4.5000 | 0 | 4 | 0.6075 |
| strict | LGBM | 4.7500 | 0 | 4 | 0.6043 |
| strict | RF | 5.5000 | 0 | 4 | 0.6023 |
| strict | LSTM | 6.0000 | 0 | 4 | 0.6007 |
| strict | LR | 6.2500 | 1 | 4 | 0.5793 |


Wilcoxon signed-rank, proposed vs each baseline

| protocol | comparison | n_tasks | mean_auc_diff | proposed_better | proposed_worse | wilcoxon_W | p_raw | p_holm | nemenyi_significant |
|---|---|---|---|---|---|---|---|---|---|
| benchmark | Stack (proposed) vs LR | 10 | 0.0610 | 7 | 3 | 13.0000 | 0.1602 | 0.4805 | False |
| benchmark | Stack (proposed) vs RF | 10 | 0.0116 | 8 | 2 | 10.0000 | 0.0840 | 0.3359 | False |
| benchmark | Stack (proposed) vs XGB | 10 | 0.0053 | 8 | 2 | 16.0000 | 0.2754 | 0.4805 | False |
| benchmark | Stack (proposed) vs LGBM | 10 | 0.0165 | 9 | 1 | 5.0000 | 0.0195 | 0.0977 | False |
| benchmark | Stack (proposed) vs CatBoost | 10 | 0.0008 | 8 | 2 | 13.0000 | 0.1602 | 0.4805 | False |
| benchmark | Stack (proposed) vs LSTM | 10 | 0.0296 | 9 | 1 | 2.0000 | 0.0059 | 0.0410 | False |
| benchmark | Stack (proposed) vs Transformer | 10 | 0.0288 | 9 | 1 | 2.0000 | 0.0059 | 0.0410 | False |
| strict | Stack (proposed) vs LR | 4 | 0.0545 | 3 | 1 | 1.0000 | 0.2500 | 0.8750 | False |
| strict | Stack (proposed) vs RF | 4 | 0.0315 | 4 | 0 | 0.0000 | 0.1250 | 0.8750 | False |
| strict | Stack (proposed) vs XGB | 4 | 0.0252 | 4 | 0 | 0.0000 | 0.1250 | 0.8750 | False |
| strict | Stack (proposed) vs LGBM | 4 | 0.0295 | 4 | 0 | 0.0000 | 0.1250 | 0.8750 | False |
| strict | Stack (proposed) vs CatBoost | 4 | -0.0036 | 2 | 2 | 4.0000 | 0.8750 | 0.8750 | False |
| strict | Stack (proposed) vs LSTM | 4 | 0.0331 | 4 | 0 | 0.0000 | 0.1250 | 0.8750 | False |
| strict | Stack (proposed) vs Transformer | 4 | 0.0263 | 4 | 0 | 0.0000 | 0.1250 | 0.8750 | False |


Nemenyi pairwise p-values (BENCHMARK)

| model | LR | RF | XGB | LGBM | CatBoost | LSTM | Transformer | Stack (proposed) |
|---|---|---|---|---|---|---|---|---|
| LR | 1.0000 | 1.0000 | 0.9580 | 0.9983 | 0.9359 | 1.0000 | 1.0000 | 0.0877 |
| RF | 1.0000 | 1.0000 | 0.9920 | 1.0000 | 0.9849 | 0.9998 | 1.0000 | 0.1723 |
| XGB | 0.9580 | 0.9920 | 1.0000 | 0.9998 | 1.0000 | 0.9072 | 0.9580 | 0.6645 |
| LGBM | 0.9983 | 1.0000 | 0.9998 | 1.0000 | 0.9994 | 0.9920 | 0.9983 | 0.3571 |
| CatBoost | 0.9359 | 0.9849 | 1.0000 | 0.9994 | 1.0000 | 0.8713 | 0.9359 | 0.7239 |
| LSTM | 1.0000 | 0.9998 | 0.9072 | 0.9920 | 0.8713 | 1.0000 | 1.0000 | 0.0528 |
| Transformer | 1.0000 | 1.0000 | 0.9580 | 0.9983 | 0.9359 | 1.0000 | 1.0000 | 0.0877 |
| Stack (proposed) | 0.0877 | 0.1723 | 0.6645 | 0.3571 | 0.7239 | 0.0528 | 0.0877 | 1.0000 |


### Per-task paired tests: proposed vs best baseline (best = highest mean test AUC among the 7 baselines; seed-0 predictions)

DeLong assumes independent prefixes (prefixes of the same case are correlated, so DeLong p-values are optimistic); the paired case-cluster bootstrap (1,000 resamples of cases, same resample for both models) respects the clustering.

| protocol | task | comparison | auc_proposed | auc_baseline | delta | delong_z | delong_p | boot_delta_ci_lo | boot_delta_ci_hi | boot_p_two_sided |
|---|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | Stack (proposed) vs CatBoost | 0.7008 | 0.6966 | 0.0042 | 5.5162 | 0.0000 | -0.0012 | 0.0095 | 0.1340 |
| benchmark | bpic2012_cancelled | Stack (proposed) vs RF | 0.7245 | 0.7338 | -0.0094 | -4.2001 | 0.0000 | -0.0240 | 0.0062 | 0.2040 |
| benchmark | bpic2012_declined | Stack (proposed) vs XGB | 0.5904 | 0.6078 | -0.0174 | -6.2648 | 0.0000 | -0.0387 | 0.0040 | 0.1340 |
| benchmark | bpic2017_accepted | Stack (proposed) vs LGBM | 0.8996 | 0.8994 | 0.0001 | 1.2207 | 0.2222 | -0.0004 | 0.0006 | 0.6180 |
| benchmark | bpic2017_cancelled | Stack (proposed) vs LGBM | 0.8645 | 0.8642 | 0.0002 | 1.6649 | 0.0959 | -0.0007 | 0.0012 | 0.5980 |
| benchmark | bpic2017_refused | Stack (proposed) vs LGBM | 0.8552 | 0.8545 | 0.0007 | 2.1442 | 0.0320 | -0.0013 | 0.0027 | 0.5260 |
| benchmark | sepsis_cases_1 | Stack (proposed) vs LR | 0.3770 | 0.5037 | -0.1267 | -5.8096 | 0.0000 | -0.3143 | 0.0543 | 0.1580 |
| benchmark | sepsis_cases_2 | Stack (proposed) vs LR | 0.8185 | 0.8855 | -0.0671 | -4.2026 | 0.0000 | -0.1599 | 0.0242 | 0.1560 |
| benchmark | sepsis_cases_3 | Stack (proposed) vs LR | 0.7253 | 0.7038 | 0.0216 | 1.4166 | 0.1566 | -0.0720 | 0.1204 | 0.6880 |
| benchmark | traffic_fines_1 | Stack (proposed) vs LR | 0.7953 | 0.7935 | 0.0018 | 3.0140 | 0.0026 | 0.0001 | 0.0034 | 0.0420 |
| strict | bpic2012_accepted | Stack (proposed) vs CatBoost | 0.5518 | 0.5744 | -0.0226 | -5.1766 | 0.0000 | -0.0497 | 0.0037 | 0.1040 |
| strict | bpic2017_accepted | Stack (proposed) vs LGBM | 0.6808 | 0.6803 | 0.0005 | 2.4121 | 0.0159 | -0.0009 | 0.0020 | 0.4640 |
| strict | sepsis_cases_1 | Stack (proposed) vs LR | 0.5078 | 0.5280 | -0.0201 | -0.9991 | 0.3178 | -0.1726 | 0.1252 | 0.7900 |
| strict | traffic_fines_1 | Stack (proposed) vs Transformer | 0.7927 | 0.7911 | 0.0017 | 6.4491 | 0.0000 | 0.0010 | 0.0022 | 0.0000 |


All pairwise per-task tests are in `ALL_pairwise_tests.csv`.

## 6. Calibration

Calibrator chosen for the stack (per seed 0..4) by cross-validated log-loss on validation part A:

| protocol | task | chosen_calibrator |
|---|---|---|
| benchmark | bpic2012_accepted | none, none, none, none, none |
| benchmark | bpic2012_cancelled | none, none, none, none, none |
| benchmark | bpic2012_declined | none, none, none, none, none |
| benchmark | bpic2017_accepted | none, none, none, none, none |
| benchmark | bpic2017_cancelled | none, none, none, none, none |
| benchmark | bpic2017_refused | none, none, none, venn-abers, none |
| benchmark | sepsis_cases_1 | none, venn-abers, platt, none, platt |
| benchmark | sepsis_cases_2 | none, none, none, none, none |
| benchmark | sepsis_cases_3 | none, none, none, none, none |
| benchmark | traffic_fines_1 | isotonic, isotonic, venn-abers, venn-abers, isotonic |
| strict | bpic2012_accepted | none, none, none, none, none |
| strict | bpic2017_accepted | none, none, none, none, none |
| strict | sepsis_cases_1 | none, none, platt, platt, venn-abers |
| strict | traffic_fines_1 | venn-abers, venn-abers, venn-abers, venn-abers, venn-abers |


Meta-learner weights on base-model log-odds (mean over seeds):

| protocol | task | meta_w_LGBM | meta_w_XGB | meta_w_CatBoost | meta_w_Transformer |
|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | 0.368 | 0.348 | 0.609 | 0.150 |
| benchmark | bpic2012_cancelled | 0.164 | 0.504 | 1.003 | 0.434 |
| benchmark | bpic2012_declined | 0.492 | 0.630 | 0.034 | 0.592 |
| benchmark | bpic2017_accepted | 0.390 | 0.162 | 0.534 | 0.024 |
| benchmark | bpic2017_cancelled | 0.524 | 0.011 | 0.717 | 0.049 |
| benchmark | bpic2017_refused | 2.394 | -0.762 | 0.855 | -0.001 |
| benchmark | sepsis_cases_1 | 0.521 | 1.045 | 1.771 | 0.032 |
| benchmark | sepsis_cases_2 | 0.221 | 0.581 | 1.378 | -0.069 |
| benchmark | sepsis_cases_3 | 0.223 | 0.859 | 0.246 | 0.767 |
| benchmark | traffic_fines_1 | -0.126 | 0.090 | 0.726 | 0.360 |
| strict | bpic2012_accepted | -0.228 | 0.730 | 0.477 | 0.111 |
| strict | bpic2017_accepted | 0.495 | 0.401 | 0.115 | 0.021 |
| strict | sepsis_cases_1 | -0.214 | 0.055 | 0.524 | 0.475 |
| strict | traffic_fines_1 | 0.075 | 0.298 | 0.069 | 0.606 |


Calibrator comparison (fit on validation part A, evaluated on test; mean over seeds). ECE uses 15 equal-width bins.


BENCHMARK ECE by calibrator

| task | model | beta | chosen post-calibration [isotonic] | chosen post-calibration [none] | chosen post-calibration [platt] | chosen post-calibration [venn-abers] | isotonic | meta-LR output (no post-calibration) | none | platt | venn-abers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | CatBoost | 0.0430 |  |  |  |  | 0.0357 |  | 0.0468 | 0.0446 | 0.0369 |
| bpic2012_accepted | LGBM | 0.0446 |  |  |  |  | 0.0372 |  | 0.0669 | 0.0448 | 0.0387 |
| bpic2012_accepted | LSTM | 0.0381 |  |  |  |  | 0.0353 |  | 0.0560 | 0.0371 | 0.0365 |
| bpic2012_accepted | RF | 0.0283 |  |  |  |  | 0.0289 |  | 0.0726 | 0.0268 | 0.0296 |
| bpic2012_accepted | Stack (proposed) |  |  | 0.0459 |  |  |  | 0.0459 |  |  |  |
| bpic2012_accepted | Transformer | 0.0360 |  |  |  |  | 0.0369 |  | 0.0528 | 0.0321 | 0.0385 |
| bpic2012_accepted | XGB | 0.0389 |  |  |  |  | 0.0450 |  | 0.0757 | 0.0339 | 0.0424 |
| bpic2012_cancelled | CatBoost | 0.0447 |  |  |  |  | 0.0438 |  | 0.1515 | 0.0456 | 0.0471 |
| bpic2012_cancelled | LGBM | 0.0550 |  |  |  |  | 0.0487 |  | 0.0978 | 0.0545 | 0.0504 |
| bpic2012_cancelled | LSTM | 0.0447 |  |  |  |  | 0.0450 |  | 0.0745 | 0.0441 | 0.0463 |
| bpic2012_cancelled | RF | 0.0532 |  |  |  |  | 0.0453 |  | 0.1105 | 0.0511 | 0.0495 |
| bpic2012_cancelled | Stack (proposed) |  |  | 0.0481 |  |  |  | 0.0481 |  |  |  |
| bpic2012_cancelled | Transformer | 0.0447 |  |  |  |  | 0.0452 |  | 0.0516 | 0.0441 | 0.0449 |
| bpic2012_cancelled | XGB | 0.0627 |  |  |  |  | 0.0468 |  | 0.0868 | 0.0496 | 0.0492 |
| bpic2012_declined | CatBoost | 0.0286 |  |  |  |  | 0.0334 |  | 0.0611 | 0.0280 | 0.0346 |
| bpic2012_declined | LGBM | 0.0435 |  |  |  |  | 0.0444 |  | 0.0466 | 0.0444 | 0.0447 |
| bpic2012_declined | LSTM | 0.0291 |  |  |  |  | 0.0208 |  | 0.0354 | 0.0299 | 0.0205 |
| bpic2012_declined | RF | 0.0454 |  |  |  |  | 0.0382 |  | 0.0847 | 0.0475 | 0.0392 |
| bpic2012_declined | Stack (proposed) |  |  | 0.0394 |  |  |  | 0.0394 |  |  |  |
| bpic2012_declined | Transformer | 0.0275 |  |  |  |  | 0.0247 |  | 0.0269 | 0.0298 | 0.0241 |
| bpic2012_declined | XGB | 0.0247 |  |  |  |  | 0.0311 |  | 0.0260 | 0.0246 | 0.0327 |
| bpic2017_accepted | CatBoost | 0.0148 |  |  |  |  | 0.0182 |  | 0.0201 | 0.0141 | 0.0196 |
| bpic2017_accepted | LGBM | 0.0133 |  |  |  |  | 0.0146 |  | 0.0303 | 0.0130 | 0.0155 |
| bpic2017_accepted | LSTM | 0.0181 |  |  |  |  | 0.0144 |  | 0.0188 | 0.0204 | 0.0161 |
| bpic2017_accepted | RF | 0.0178 |  |  |  |  | 0.0145 |  | 0.0168 | 0.0183 | 0.0162 |
| bpic2017_accepted | Stack (proposed) |  |  | 0.0134 |  |  |  | 0.0134 |  |  |  |
| bpic2017_accepted | Transformer | 0.0157 |  |  |  |  | 0.0155 |  | 0.0250 | 0.0161 | 0.0158 |
| bpic2017_accepted | XGB | 0.0154 |  |  |  |  | 0.0153 |  | 0.0339 | 0.0148 | 0.0169 |
| bpic2017_cancelled | CatBoost | 0.0111 |  |  |  |  | 0.0119 |  | 0.0290 | 0.0118 | 0.0118 |
| bpic2017_cancelled | LGBM | 0.0157 |  |  |  |  | 0.0149 |  | 0.0533 | 0.0159 | 0.0153 |
| bpic2017_cancelled | LSTM | 0.0260 |  |  |  |  | 0.0218 |  | 0.0312 | 0.0251 | 0.0216 |
| bpic2017_cancelled | RF | 0.0298 |  |  |  |  | 0.0137 |  | 0.0320 | 0.0318 | 0.0147 |
| bpic2017_cancelled | Stack (proposed) |  |  | 0.0130 |  |  |  | 0.0130 |  |  |  |
| bpic2017_cancelled | Transformer | 0.0233 |  |  |  |  | 0.0206 |  | 0.0312 | 0.0234 | 0.0211 |
| bpic2017_cancelled | XGB | 0.0189 |  |  |  |  | 0.0152 |  | 0.0295 | 0.0193 | 0.0152 |
| bpic2017_refused | CatBoost | 0.0142 |  |  |  |  | 0.0160 |  | 0.0695 | 0.0142 | 0.0170 |
| bpic2017_refused | LGBM | 0.0555 |  |  |  |  | 0.0170 |  | 0.0627 | 0.0312 | 0.0182 |
| bpic2017_refused | LSTM | 0.0137 |  |  |  |  | 0.0174 |  | 0.0187 | 0.0161 | 0.0163 |
| bpic2017_refused | RF | 0.0194 |  |  |  |  | 0.0183 |  | 0.0201 | 0.0197 | 0.0202 |
| bpic2017_refused | Stack (proposed) |  |  | 0.0170 |  | 0.0188 |  | 0.0168 |  |  |  |
| bpic2017_refused | Transformer | 0.0157 |  |  |  |  | 0.0206 |  | 0.0135 | 0.0220 | 0.0201 |
| bpic2017_refused | XGB | 0.0498 |  |  |  |  | 0.0168 |  | 0.0574 | 0.0281 | 0.0167 |
| sepsis_cases_1 | CatBoost | 0.2013 |  |  |  |  | 0.1816 |  | 0.2013 | 0.1644 | 0.1815 |
| sepsis_cases_1 | LGBM | 0.1200 |  |  |  |  | 0.1817 |  | 0.0575 | 0.1332 | 0.1804 |
| sepsis_cases_1 | LSTM | 0.1223 |  |  |  |  | 0.1110 |  | 0.1223 | 0.1348 | 0.1163 |
| sepsis_cases_1 | RF | 0.1405 |  |  |  |  | 0.1668 |  | 0.1218 | 0.1392 | 0.1601 |
| sepsis_cases_1 | Stack (proposed) |  |  | 0.1602 | 0.1292 | 0.0998 |  | 0.1705 |  |  |  |
| sepsis_cases_1 | Transformer | 0.1126 |  |  |  |  | 0.1289 |  | 0.0905 | 0.1281 | 0.1310 |
| sepsis_cases_1 | XGB | 0.0971 |  |  |  |  | 0.1746 |  | 0.0716 | 0.1535 | 0.1727 |
| sepsis_cases_2 | CatBoost | 0.0873 |  |  |  |  | 0.0953 |  | 0.0447 | 0.0870 | 0.0821 |
| sepsis_cases_2 | LGBM | 0.0366 |  |  |  |  | 0.0407 |  | 0.0633 | 0.0397 | 0.0410 |
| sepsis_cases_2 | LSTM | 0.0331 |  |  |  |  | 0.0332 |  | 0.0405 | 0.0297 | 0.0319 |
| sepsis_cases_2 | RF | 0.0295 |  |  |  |  | 0.0204 |  | 0.0491 | 0.0255 | 0.0172 |
| sepsis_cases_2 | Stack (proposed) |  |  | 0.0843 |  |  |  | 0.0843 |  |  |  |
| sepsis_cases_2 | Transformer | 0.0347 |  |  |  |  | 0.0342 |  | 0.0329 | 0.0295 | 0.0287 |
| sepsis_cases_2 | XGB | 0.0489 |  |  |  |  | 0.0470 |  | 0.0812 | 0.0334 | 0.0442 |
| sepsis_cases_3 | CatBoost | 0.0869 |  |  |  |  | 0.0684 |  | 0.0931 | 0.0786 | 0.0646 |
| sepsis_cases_3 | LGBM | 0.0598 |  |  |  |  | 0.0612 |  | 0.0506 | 0.0614 | 0.0577 |
| sepsis_cases_3 | LSTM | 0.0514 |  |  |  |  | 0.0661 |  | 0.0514 | 0.0321 | 0.0628 |
| sepsis_cases_3 | RF | 0.0922 |  |  |  |  | 0.0981 |  | 0.0460 | 0.0951 | 0.0846 |
| sepsis_cases_3 | Stack (proposed) |  |  | 0.0627 |  |  |  | 0.0627 |  |  |  |
| sepsis_cases_3 | Transformer | 0.0738 |  |  |  |  | 0.0613 |  | 0.0738 | 0.0445 | 0.0637 |
| sepsis_cases_3 | XGB | 0.0535 |  |  |  |  | 0.0854 |  | 0.0416 | 0.0778 | 0.0820 |
| traffic_fines_1 | CatBoost | 0.0792 |  |  |  |  | 0.0751 |  | 0.0654 | 0.0823 | 0.0748 |
| traffic_fines_1 | LGBM | 0.0797 |  |  |  |  | 0.0728 |  | 0.0797 | 0.0790 | 0.0728 |
| traffic_fines_1 | LSTM | 0.0518 |  |  |  |  | 0.0444 |  | 0.0482 | 0.0589 | 0.0467 |
| traffic_fines_1 | RF | 0.0513 |  |  |  |  | 0.0526 |  | 0.0513 | 0.0610 | 0.0535 |
| traffic_fines_1 | Stack (proposed) |  | 0.0653 |  |  | 0.0718 |  | 0.0714 |  |  |  |
| traffic_fines_1 | Transformer | 0.0480 |  |  |  |  | 0.0402 |  | 0.0661 | 0.0552 | 0.0396 |
| traffic_fines_1 | XGB | 0.0617 |  |  |  |  | 0.0720 |  | 0.0647 | 0.0752 | 0.0714 |


BENCHMARK Brier by calibrator

| task | model | beta | chosen post-calibration [isotonic] | chosen post-calibration [none] | chosen post-calibration [platt] | chosen post-calibration [venn-abers] | isotonic | meta-LR output (no post-calibration) | none | platt | venn-abers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | CatBoost | 0.2133 |  |  |  |  | 0.2133 |  | 0.2141 | 0.2134 | 0.2131 |
| bpic2012_accepted | LGBM | 0.2136 |  |  |  |  | 0.2137 |  | 0.2166 | 0.2137 | 0.2136 |
| bpic2012_accepted | LSTM | 0.2133 |  |  |  |  | 0.2129 |  | 0.2156 | 0.2131 | 0.2129 |
| bpic2012_accepted | RF | 0.2168 |  |  |  |  | 0.2169 |  | 0.2214 | 0.2167 | 0.2168 |
| bpic2012_accepted | Stack (proposed) |  |  | 0.2115 |  |  |  | 0.2115 |  |  |  |
| bpic2012_accepted | Transformer | 0.2190 |  |  |  |  | 0.2191 |  | 0.2206 | 0.2184 | 0.2191 |
| bpic2012_accepted | XGB | 0.2130 |  |  |  |  | 0.2145 |  | 0.2181 | 0.2124 | 0.2139 |
| bpic2012_cancelled | CatBoost | 0.1606 |  |  |  |  | 0.1614 |  | 0.1857 | 0.1608 | 0.1617 |
| bpic2012_cancelled | LGBM | 0.1625 |  |  |  |  | 0.1612 |  | 0.1700 | 0.1622 | 0.1613 |
| bpic2012_cancelled | LSTM | 0.1603 |  |  |  |  | 0.1599 |  | 0.1648 | 0.1601 | 0.1600 |
| bpic2012_cancelled | RF | 0.1624 |  |  |  |  | 0.1609 |  | 0.1707 | 0.1613 | 0.1615 |
| bpic2012_cancelled | Stack (proposed) |  |  | 0.1603 |  |  |  | 0.1603 |  |  |  |
| bpic2012_cancelled | Transformer | 0.1649 |  |  |  |  | 0.1646 |  | 0.1661 | 0.1647 | 0.1646 |
| bpic2012_cancelled | XGB | 0.1670 |  |  |  |  | 0.1637 |  | 0.1706 | 0.1640 | 0.1638 |
| bpic2012_declined | CatBoost | 0.1451 |  |  |  |  | 0.1454 |  | 0.1491 | 0.1451 | 0.1455 |
| bpic2012_declined | LGBM | 0.1477 |  |  |  |  | 0.1481 |  | 0.1488 | 0.1480 | 0.1478 |
| bpic2012_declined | LSTM | 0.1447 |  |  |  |  | 0.1444 |  | 0.1461 | 0.1450 | 0.1443 |
| bpic2012_declined | RF | 0.1475 |  |  |  |  | 0.1472 |  | 0.1560 | 0.1482 | 0.1476 |
| bpic2012_declined | Stack (proposed) |  |  | 0.1458 |  |  |  | 0.1458 |  |  |  |
| bpic2012_declined | Transformer | 0.1483 |  |  |  |  | 0.1481 |  | 0.1485 | 0.1486 | 0.1484 |
| bpic2012_declined | XGB | 0.1441 |  |  |  |  | 0.1443 |  | 0.1447 | 0.1441 | 0.1446 |
| bpic2017_accepted | CatBoost | 0.1201 |  |  |  |  | 0.1204 |  | 0.1202 | 0.1200 | 0.1203 |
| bpic2017_accepted | LGBM | 0.1196 |  |  |  |  | 0.1197 |  | 0.1206 | 0.1196 | 0.1196 |
| bpic2017_accepted | LSTM | 0.1299 |  |  |  |  | 0.1298 |  | 0.1303 | 0.1300 | 0.1298 |
| bpic2017_accepted | RF | 0.1230 |  |  |  |  | 0.1228 |  | 0.1230 | 0.1230 | 0.1228 |
| bpic2017_accepted | Stack (proposed) |  |  | 0.1195 |  |  |  | 0.1195 |  |  |  |
| bpic2017_accepted | Transformer | 0.1296 |  |  |  |  | 0.1299 |  | 0.1306 | 0.1297 | 0.1298 |
| bpic2017_accepted | XGB | 0.1199 |  |  |  |  | 0.1198 |  | 0.1214 | 0.1199 | 0.1198 |
| bpic2017_cancelled | CatBoost | 0.1447 |  |  |  |  | 0.1451 |  | 0.1455 | 0.1447 | 0.1450 |
| bpic2017_cancelled | LGBM | 0.1449 |  |  |  |  | 0.1452 |  | 0.1494 | 0.1449 | 0.1450 |
| bpic2017_cancelled | LSTM | 0.1817 |  |  |  |  | 0.1818 |  | 0.1824 | 0.1818 | 0.1818 |
| bpic2017_cancelled | RF | 0.1491 |  |  |  |  | 0.1482 |  | 0.1494 | 0.1494 | 0.1482 |
| bpic2017_cancelled | Stack (proposed) |  |  | 0.1446 |  |  |  | 0.1446 |  |  |  |
| bpic2017_cancelled | Transformer | 0.1806 |  |  |  |  | 0.1808 |  | 0.1815 | 0.1807 | 0.1808 |
| bpic2017_cancelled | XGB | 0.1463 |  |  |  |  | 0.1467 |  | 0.1469 | 0.1463 | 0.1464 |
| bpic2017_refused | CatBoost | 0.0745 |  |  |  |  | 0.0742 |  | 0.0833 | 0.0745 | 0.0743 |
| bpic2017_refused | LGBM | 0.0896 |  |  |  |  | 0.0739 |  | 0.0956 | 0.0748 | 0.0741 |
| bpic2017_refused | LSTM | 0.1031 |  |  |  |  | 0.1033 |  | 0.1033 | 0.1032 | 0.1032 |
| bpic2017_refused | RF | 0.0761 |  |  |  |  | 0.0758 |  | 0.0774 | 0.0766 | 0.0761 |
| bpic2017_refused | Stack (proposed) |  |  | 0.0739 |  | 0.0741 |  | 0.0739 |  |  |  |
| bpic2017_refused | Transformer | 0.1026 |  |  |  |  | 0.1029 |  | 0.1025 | 0.1028 | 0.1028 |
| bpic2017_refused | XGB | 0.0865 |  |  |  |  | 0.0739 |  | 0.0928 | 0.0747 | 0.0738 |
| sepsis_cases_1 | CatBoost | 0.1445 |  |  |  |  | 0.1467 |  | 0.1445 | 0.1393 | 0.1471 |
| sepsis_cases_1 | LGBM | 0.1283 |  |  |  |  | 0.1515 |  | 0.1010 | 0.1348 | 0.1508 |
| sepsis_cases_1 | LSTM | 0.1199 |  |  |  |  | 0.1155 |  | 0.1199 | 0.1216 | 0.1161 |
| sepsis_cases_1 | RF | 0.1268 |  |  |  |  | 0.1517 |  | 0.1160 | 0.1239 | 0.1417 |
| sepsis_cases_1 | Stack (proposed) |  |  | 0.1406 | 0.1218 | 0.1050 |  | 0.1421 |  |  |  |
| sepsis_cases_1 | Transformer | 0.1166 |  |  |  |  | 0.1315 |  | 0.1123 | 0.1190 | 0.1310 |
| sepsis_cases_1 | XGB | 0.1132 |  |  |  |  | 0.1590 |  | 0.1050 | 0.1319 | 0.1536 |
| sepsis_cases_2 | CatBoost | 0.0898 |  |  |  |  | 0.0904 |  | 0.0618 | 0.0896 | 0.0801 |
| sepsis_cases_2 | LGBM | 0.0608 |  |  |  |  | 0.0603 |  | 0.0679 | 0.0613 | 0.0597 |
| sepsis_cases_2 | LSTM | 0.0725 |  |  |  |  | 0.0768 |  | 0.0740 | 0.0718 | 0.0758 |
| sepsis_cases_2 | RF | 0.0588 |  |  |  |  | 0.0601 |  | 0.0625 | 0.0569 | 0.0585 |
| sepsis_cases_2 | Stack (proposed) |  |  | 0.0873 |  |  |  | 0.0873 |  |  |  |
| sepsis_cases_2 | Transformer | 0.0700 |  |  |  |  | 0.0742 |  | 0.0697 | 0.0675 | 0.0711 |
| sepsis_cases_2 | XGB | 0.0551 |  |  |  |  | 0.0507 |  | 0.0685 | 0.0496 | 0.0501 |
| sepsis_cases_3 | CatBoost | 0.1465 |  |  |  |  | 0.1523 |  | 0.1452 | 0.1432 | 0.1486 |
| sepsis_cases_3 | LGBM | 0.1475 |  |  |  |  | 0.1515 |  | 0.1436 | 0.1473 | 0.1501 |
| sepsis_cases_3 | LSTM | 0.1478 |  |  |  |  | 0.1506 |  | 0.1478 | 0.1467 | 0.1496 |
| sepsis_cases_3 | RF | 0.1526 |  |  |  |  | 0.1587 |  | 0.1375 | 0.1505 | 0.1515 |
| sepsis_cases_3 | Stack (proposed) |  |  | 0.1383 |  |  |  | 0.1383 |  |  |  |
| sepsis_cases_3 | Transformer | 0.1440 |  |  |  |  | 0.1425 |  | 0.1440 | 0.1404 | 0.1423 |
| sepsis_cases_3 | XGB | 0.1490 |  |  |  |  | 0.1620 |  | 0.1451 | 0.1551 | 0.1580 |
| traffic_fines_1 | CatBoost | 0.1873 |  |  |  |  | 0.1877 |  | 0.1817 | 0.1869 | 0.1871 |
| traffic_fines_1 | LGBM | 0.1898 |  |  |  |  | 0.1894 |  | 0.1898 | 0.1849 | 0.1890 |
| traffic_fines_1 | LSTM | 0.1816 |  |  |  |  | 0.1801 |  | 0.1800 | 0.1815 | 0.1803 |
| traffic_fines_1 | RF | 0.1842 |  |  |  |  | 0.1866 |  | 0.1842 | 0.1864 | 0.1864 |
| traffic_fines_1 | Stack (proposed) |  | 0.1834 |  |  | 0.1854 |  | 0.1826 |  |  |  |
| traffic_fines_1 | Transformer | 0.1807 |  |  |  |  | 0.1794 |  | 0.1825 | 0.1807 | 0.1788 |
| traffic_fines_1 | XGB | 0.1818 |  |  |  |  | 0.1896 |  | 0.1825 | 0.1847 | 0.1891 |


STRICT ECE by calibrator

| task | model | beta | chosen post-calibration [none] | chosen post-calibration [platt] | chosen post-calibration [venn-abers] | isotonic | meta-LR output (no post-calibration) | none | platt | venn-abers |
|---|---|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | CatBoost | 0.0388 |  |  |  | 0.0367 |  | 0.0380 | 0.0382 | 0.0362 |
| bpic2012_accepted | LGBM | 0.0471 |  |  |  | 0.0422 |  | 0.0499 | 0.0470 | 0.0411 |
| bpic2012_accepted | LSTM | 0.0582 |  |  |  | 0.0386 |  | 0.0632 | 0.0324 | 0.0382 |
| bpic2012_accepted | RF | 0.0393 |  |  |  | 0.0415 |  | 0.0581 | 0.0390 | 0.0404 |
| bpic2012_accepted | Stack (proposed) |  | 0.0483 |  |  |  | 0.0483 |  |  |  |
| bpic2012_accepted | Transformer | 0.0892 |  |  |  | 0.0388 |  | 0.0892 | 0.0284 | 0.0381 |
| bpic2012_accepted | XGB | 0.0532 |  |  |  | 0.0656 |  | 0.0741 | 0.0518 | 0.0647 |
| bpic2017_accepted | CatBoost | 0.0195 |  |  |  | 0.0199 |  | 0.0287 | 0.0163 | 0.0204 |
| bpic2017_accepted | LGBM | 0.0216 |  |  |  | 0.0209 |  | 0.0263 | 0.0161 | 0.0210 |
| bpic2017_accepted | LSTM | 0.0242 |  |  |  | 0.0242 |  | 0.0337 | 0.0212 | 0.0247 |
| bpic2017_accepted | RF | 0.0252 |  |  |  | 0.0219 |  | 0.0353 | 0.0212 | 0.0227 |
| bpic2017_accepted | Stack (proposed) |  | 0.0155 |  |  |  | 0.0155 |  |  |  |
| bpic2017_accepted | Transformer | 0.0201 |  |  |  | 0.0220 |  | 0.0351 | 0.0160 | 0.0226 |
| bpic2017_accepted | XGB | 0.0189 |  |  |  | 0.0203 |  | 0.0217 | 0.0162 | 0.0201 |
| sepsis_cases_1 | CatBoost | 0.1008 |  |  |  | 0.1317 |  | 0.1008 | 0.1037 | 0.1306 |
| sepsis_cases_1 | LGBM | 0.0826 |  |  |  | 0.1598 |  | 0.0826 | 0.1123 | 0.1618 |
| sepsis_cases_1 | LSTM | 0.0772 |  |  |  | 0.1112 |  | 0.0772 | 0.1060 | 0.1179 |
| sepsis_cases_1 | RF | 0.1163 |  |  |  | 0.1428 |  | 0.1103 | 0.1227 | 0.1430 |
| sepsis_cases_1 | Stack (proposed) |  | 0.1206 | 0.0996 | 0.1059 |  | 0.1158 |  |  |  |
| sepsis_cases_1 | Transformer | 0.0961 |  |  |  | 0.1159 |  | 0.0781 | 0.1196 | 0.1210 |
| sepsis_cases_1 | XGB | 0.0769 |  |  |  | 0.1469 |  | 0.0656 | 0.1128 | 0.1500 |
| traffic_fines_1 | CatBoost | 0.0368 |  |  |  | 0.0534 |  | 0.0809 | 0.0415 | 0.0532 |
| traffic_fines_1 | LGBM | 0.1050 |  |  |  | 0.0650 |  | 0.1155 | 0.0734 | 0.0663 |
| traffic_fines_1 | LSTM | 0.0405 |  |  |  | 0.0359 |  | 0.0652 | 0.0413 | 0.0368 |
| traffic_fines_1 | RF | 0.0634 |  |  |  | 0.0598 |  | 0.0802 | 0.0683 | 0.0598 |
| traffic_fines_1 | Stack (proposed) |  |  |  | 0.0541 |  | 0.0545 |  |  |  |
| traffic_fines_1 | Transformer | 0.0406 |  |  |  | 0.0332 |  | 0.0776 | 0.0419 | 0.0337 |
| traffic_fines_1 | XGB | 0.1183 |  |  |  | 0.0809 |  | 0.1267 | 0.0775 | 0.0806 |


STRICT Brier by calibrator

| task | model | beta | chosen post-calibration [none] | chosen post-calibration [platt] | chosen post-calibration [venn-abers] | isotonic | meta-LR output (no post-calibration) | none | platt | venn-abers |
|---|---|---|---|---|---|---|---|---|---|---|
| bpic2012_accepted | CatBoost | 0.2447 |  |  |  | 0.2457 |  | 0.2451 | 0.2442 | 0.2454 |
| bpic2012_accepted | LGBM | 0.2462 |  |  |  | 0.2470 |  | 0.2468 | 0.2462 | 0.2462 |
| bpic2012_accepted | LSTM | 0.2494 |  |  |  | 0.2465 |  | 0.2500 | 0.2463 | 0.2463 |
| bpic2012_accepted | RF | 0.2474 |  |  |  | 0.2480 |  | 0.2500 | 0.2473 | 0.2477 |
| bpic2012_accepted | Stack (proposed) |  | 0.2472 |  |  |  | 0.2472 |  |  |  |
| bpic2012_accepted | Transformer | 0.2540 |  |  |  | 0.2464 |  | 0.2540 | 0.2453 | 0.2462 |
| bpic2012_accepted | XGB | 0.2485 |  |  |  | 0.2509 |  | 0.2531 | 0.2485 | 0.2505 |
| bpic2017_accepted | CatBoost | 0.2171 |  |  |  | 0.2176 |  | 0.2177 | 0.2170 | 0.2175 |
| bpic2017_accepted | LGBM | 0.2168 |  |  |  | 0.2169 |  | 0.2170 | 0.2162 | 0.2168 |
| bpic2017_accepted | LSTM | 0.2216 |  |  |  | 0.2217 |  | 0.2226 | 0.2214 | 0.2216 |
| bpic2017_accepted | RF | 0.2191 |  |  |  | 0.2191 |  | 0.2202 | 0.2189 | 0.2191 |
| bpic2017_accepted | Stack (proposed) |  | 0.2159 |  |  |  | 0.2159 |  |  |  |
| bpic2017_accepted | Transformer | 0.2203 |  |  |  | 0.2204 |  | 0.2215 | 0.2201 | 0.2204 |
| bpic2017_accepted | XGB | 0.2164 |  |  |  | 0.2168 |  | 0.2166 | 0.2163 | 0.2167 |
| sepsis_cases_1 | CatBoost | 0.1142 |  |  |  | 0.1252 |  | 0.1142 | 0.1152 | 0.1243 |
| sepsis_cases_1 | LGBM | 0.1041 |  |  |  | 0.1324 |  | 0.1041 | 0.1173 | 0.1309 |
| sepsis_cases_1 | LSTM | 0.1054 |  |  |  | 0.1167 |  | 0.1054 | 0.1096 | 0.1178 |
| sepsis_cases_1 | RF | 0.1152 |  |  |  | 0.1317 |  | 0.1120 | 0.1199 | 0.1291 |
| sepsis_cases_1 | Stack (proposed) |  | 0.1288 | 0.1094 | 0.1081 |  | 0.1215 |  |  |  |
| sepsis_cases_1 | Transformer | 0.1113 |  |  |  | 0.1240 |  | 0.1073 | 0.1155 | 0.1247 |
| sepsis_cases_1 | XGB | 0.1035 |  |  |  | 0.1228 |  | 0.1010 | 0.1125 | 0.1230 |
| traffic_fines_1 | CatBoost | 0.1849 |  |  |  | 0.1892 |  | 0.1939 | 0.1852 | 0.1890 |
| traffic_fines_1 | LGBM | 0.2048 |  |  |  | 0.1924 |  | 0.2059 | 0.1910 | 0.1926 |
| traffic_fines_1 | LSTM | 0.1843 |  |  |  | 0.1839 |  | 0.1881 | 0.1843 | 0.1840 |
| traffic_fines_1 | RF | 0.1927 |  |  |  | 0.1932 |  | 0.1956 | 0.1929 | 0.1930 |
| traffic_fines_1 | Stack (proposed) |  |  |  | 0.1860 |  | 0.1850 |  |  |  |
| traffic_fines_1 | Transformer | 0.1838 |  |  |  | 0.1831 |  | 0.1900 | 0.1838 | 0.1831 |
| traffic_fines_1 | XGB | 0.2062 |  |  |  | 0.1946 |  | 0.2073 | 0.1922 | 0.1942 |

## 7. Governance: conformal deferral

Split conformal prediction with calibration set = validation part B (temporally later than part A, earlier than test); nonconformity 1 − p̂(true class) on the calibrated stack. Mondrian = class-conditional quantiles (one per label). A case is automated when the prediction set is a singleton, deferred otherwise (empty or {0,1}). Coverage guarantees assume exchangeability, which temporal drift and within-case dependence of prefixes violate; empirical coverage is therefore reported, not assumed.


### Mondrian (class-conditional)

| protocol | task | alpha | empirical coverage | cov. class 1 | cov. class 0 | singleton (automation) rate | empty | both | accuracy on singletons |
|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | 0.0500 | 0.899 ± 0.005 | 0.9490 | 0.8370 | 0.438 ± 0.011 | 0.0000 | 0.5620 | 0.770 ± 0.007 |
| benchmark | bpic2012_accepted | 0.1000 | 0.864 ± 0.005 | 0.9180 | 0.7970 | 0.518 ± 0.007 | 0.0000 | 0.4820 | 0.737 ± 0.006 |
| benchmark | bpic2012_accepted | 0.2000 | 0.802 ± 0.007 | 0.8550 | 0.7350 | 0.655 ± 0.010 | 0.0000 | 0.3450 | 0.697 ± 0.007 |
| benchmark | bpic2012_cancelled | 0.0500 | 0.926 ± 0.005 | 0.8870 | 0.9390 | 0.461 ± 0.008 | 0.0000 | 0.5390 | 0.840 ± 0.007 |
| benchmark | bpic2012_cancelled | 0.1000 | 0.891 ± 0.009 | 0.8560 | 0.9030 | 0.533 ± 0.014 | 0.0000 | 0.4670 | 0.796 ± 0.011 |
| benchmark | bpic2012_cancelled | 0.2000 | 0.817 ± 0.011 | 0.7960 | 0.8240 | 0.672 ± 0.017 | 0.0000 | 0.3280 | 0.728 ± 0.010 |
| benchmark | bpic2012_declined | 0.0500 | 0.943 ± 0.011 | 0.8840 | 0.9570 | 0.240 ± 0.029 | 0.0000 | 0.7600 | 0.761 ± 0.031 |
| benchmark | bpic2012_declined | 0.1000 | 0.898 ± 0.009 | 0.8080 | 0.9190 | 0.358 ± 0.037 | 0.0000 | 0.6420 | 0.714 ± 0.023 |
| benchmark | bpic2012_declined | 0.2000 | 0.806 ± 0.015 | 0.6890 | 0.8340 | 0.568 ± 0.016 | 0.0000 | 0.4320 | 0.658 ± 0.031 |
| benchmark | bpic2017_accepted | 0.0500 | 0.949 ± 0.001 | 0.9380 | 0.9560 | 0.665 ± 0.003 | 0.0000 | 0.3350 | 0.923 ± 0.001 |
| benchmark | bpic2017_accepted | 0.1000 | 0.902 ± 0.003 | 0.8790 | 0.9180 | 0.779 ± 0.004 | 0.0000 | 0.2210 | 0.874 ± 0.003 |
| benchmark | bpic2017_accepted | 0.2000 | 0.814 ± 0.004 | 0.7590 | 0.8520 | 0.970 ± 0.007 | 0.0000 | 0.0300 | 0.809 ± 0.004 |
| benchmark | bpic2017_cancelled | 0.0500 | 0.950 ± 0.003 | 0.9550 | 0.9450 | 0.581 ± 0.008 | 0.0000 | 0.4190 | 0.914 ± 0.004 |
| benchmark | bpic2017_cancelled | 0.1000 | 0.910 ± 0.013 | 0.9130 | 0.9070 | 0.682 ± 0.026 | 0.0000 | 0.3180 | 0.868 ± 0.013 |
| benchmark | bpic2017_cancelled | 0.2000 | 0.811 ± 0.006 | 0.8550 | 0.7730 | 0.889 ± 0.012 | 0.0000 | 0.1110 | 0.788 ± 0.004 |
| benchmark | bpic2017_refused | 0.0500 | 0.947 ± 0.003 | 0.9710 | 0.9440 | 0.478 ± 0.012 | 0.0000 | 0.5220 | 0.890 ± 0.007 |
| benchmark | bpic2017_refused | 0.1000 | 0.889 ± 0.029 | 0.9410 | 0.8810 | 0.620 ± 0.048 | 0.0000 | 0.3800 | 0.822 ± 0.036 |
| benchmark | bpic2017_refused | 0.2000 | 0.786 ± 0.037 | 0.8770 | 0.7730 | 0.818 ± 0.097 | 0.0000 | 0.1820 | 0.739 ± 0.021 |
| benchmark | sepsis_cases_1 | 0.0500 | 0.865 ± 0.079 | 0.8140 | 0.8710 | 0.218 ± 0.124 | 0.0000 | 0.7820 | 0.353 ± 0.100 |
| benchmark | sepsis_cases_1 | 0.1000 | 0.730 ± 0.063 | 0.7790 | 0.7240 | 0.400 ± 0.105 | 0.0000 | 0.6000 | 0.311 ± 0.145 |
| benchmark | sepsis_cases_1 | 0.2000 | 0.576 ± 0.103 | 0.7250 | 0.5580 | 0.619 ± 0.193 | 0.0000 | 0.3810 | 0.287 ± 0.135 |
| benchmark | sepsis_cases_2 | 0.0500 | 0.868 ± 0.050 | 0.7090 | 0.8860 | 0.867 ± 0.100 | 0.0000 | 0.1330 | 0.849 ± 0.049 |
| benchmark | sepsis_cases_2 | 0.1000 | 0.802 ± 0.048 | 0.6640 | 0.8170 | 0.918 ± 0.016 | 0.0500 | 0.0320 | 0.839 ± 0.025 |
| benchmark | sepsis_cases_2 | 0.2000 | 0.719 ± 0.061 | 0.6420 | 0.7280 | 0.865 ± 0.092 | 0.1350 | 0.0000 | 0.833 ± 0.038 |
| benchmark | sepsis_cases_3 | 0.0500 | 0.938 ± 0.016 | 0.9370 | 0.9410 | 0.275 ± 0.038 | 0.0000 | 0.7250 | 0.773 ± 0.053 |
| benchmark | sepsis_cases_3 | 0.1000 | 0.857 ± 0.028 | 0.8440 | 0.9120 | 0.435 ± 0.066 | 0.0000 | 0.5650 | 0.670 ± 0.046 |
| benchmark | sepsis_cases_3 | 0.2000 | 0.731 ± 0.030 | 0.7000 | 0.8660 | 0.646 ± 0.079 | 0.0000 | 0.3540 | 0.582 ± 0.022 |
| benchmark | traffic_fines_1 | 0.0500 | 0.946 ± 0.026 | 0.9870 | 0.9100 | 0.399 ± 0.092 | 0.0000 | 0.6010 | 0.873 ± 0.039 |
| benchmark | traffic_fines_1 | 0.1000 | 0.892 ± 0.027 | 0.9870 | 0.8080 | 0.592 ± 0.093 | 0.0000 | 0.4080 | 0.821 ± 0.022 |
| benchmark | traffic_fines_1 | 0.2000 | 0.816 ± 0.015 | 0.9480 | 0.6980 | 0.786 ± 0.030 | 0.0000 | 0.2140 | 0.766 ± 0.011 |
| strict | bpic2012_accepted | 0.0500 | 0.935 ± 0.009 | 0.9500 | 0.9190 | 0.185 ± 0.019 | 0.0000 | 0.8150 | 0.650 ± 0.023 |
| strict | bpic2012_accepted | 0.1000 | 0.888 ± 0.008 | 0.9110 | 0.8640 | 0.289 ± 0.013 | 0.0000 | 0.7110 | 0.613 ± 0.019 |
| strict | bpic2012_accepted | 0.2000 | 0.801 ± 0.006 | 0.8340 | 0.7650 | 0.482 ± 0.016 | 0.0000 | 0.5180 | 0.586 ± 0.015 |
| strict | bpic2017_accepted | 0.0500 | 0.943 ± 0.001 | 0.9330 | 0.9500 | 0.268 ± 0.005 | 0.0000 | 0.7320 | 0.788 ± 0.002 |
| strict | bpic2017_accepted | 0.1000 | 0.884 ± 0.002 | 0.8740 | 0.8910 | 0.430 ± 0.003 | 0.0000 | 0.5700 | 0.731 ± 0.002 |
| strict | bpic2017_accepted | 0.2000 | 0.790 ± 0.001 | 0.7760 | 0.8000 | 0.648 ± 0.003 | 0.0000 | 0.3520 | 0.677 ± 0.001 |
| strict | sepsis_cases_1 | 0.0500 | 0.916 ± 0.035 | 0.9330 | 0.9140 | 0.159 ± 0.068 | 0.0000 | 0.8410 | 0.404 ± 0.264 |
| strict | sepsis_cases_1 | 0.1000 | 0.867 ± 0.070 | 0.8510 | 0.8680 | 0.295 ± 0.186 | 0.0000 | 0.7050 | 0.477 ± 0.223 |
| strict | sepsis_cases_1 | 0.2000 | 0.786 ± 0.106 | 0.7840 | 0.7860 | 0.437 ± 0.237 | 0.0000 | 0.5630 | 0.491 ± 0.078 |
| strict | traffic_fines_1 | 0.0500 | 0.932 ± 0.007 | 0.9870 | 0.8910 | 0.437 ± 0.021 | 0.0000 | 0.5630 | 0.844 ± 0.008 |
| strict | traffic_fines_1 | 0.1000 | 0.870 ± 0.013 | 0.9820 | 0.7870 | 0.591 ± 0.028 | 0.0000 | 0.4090 | 0.780 ± 0.012 |
| strict | traffic_fines_1 | 0.2000 | 0.795 ± 0.003 | 0.9170 | 0.7050 | 0.779 ± 0.015 | 0.0000 | 0.2210 | 0.737 ± 0.004 |


### marginal split conformal

| protocol | task | alpha | empirical coverage | cov. class 1 | cov. class 0 | singleton (automation) rate | empty | both | accuracy on singletons |
|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | 0.0500 | 0.904 ± 0.003 | 0.9320 | 0.8690 | 0.427 ± 0.006 | 0.0000 | 0.5730 | 0.775 ± 0.005 |
| benchmark | bpic2012_accepted | 0.1000 | 0.866 ± 0.005 | 0.8750 | 0.8550 | 0.508 ± 0.008 | 0.0000 | 0.4920 | 0.737 ± 0.007 |
| benchmark | bpic2012_accepted | 0.2000 | 0.784 ± 0.005 | 0.7570 | 0.8170 | 0.681 ± 0.007 | 0.0000 | 0.3190 | 0.682 ± 0.005 |
| benchmark | bpic2012_cancelled | 0.0500 | 0.954 ± 0.002 | 0.8240 | 0.9980 | 0.441 ± 0.009 | 0.0000 | 0.5590 | 0.895 ± 0.002 |
| benchmark | bpic2012_cancelled | 0.1000 | 0.929 ± 0.004 | 0.7270 | 0.9980 | 0.532 ± 0.017 | 0.0000 | 0.4680 | 0.866 ± 0.004 |
| benchmark | bpic2012_cancelled | 0.2000 | 0.874 ± 0.006 | 0.5200 | 0.9960 | 0.708 ± 0.018 | 0.0000 | 0.2920 | 0.823 ± 0.004 |
| benchmark | bpic2012_declined | 0.0500 | 0.923 ± 0.006 | 0.5980 | 1.0000 | 0.491 ± 0.030 | 0.0000 | 0.5090 | 0.844 ± 0.010 |
| benchmark | bpic2012_declined | 0.1000 | 0.879 ± 0.007 | 0.3640 | 1.0000 | 0.736 ± 0.025 | 0.0000 | 0.2640 | 0.835 ± 0.004 |
| benchmark | bpic2012_declined | 0.2000 | 0.799 ± 0.006 | 0.0720 | 0.9700 | 0.969 ± 0.008 | 0.0310 | 0.0000 | 0.824 ± 0.001 |
| benchmark | bpic2017_accepted | 0.0500 | 0.949 ± 0.001 | 0.9310 | 0.9620 | 0.666 ± 0.004 | 0.0000 | 0.3340 | 0.924 ± 0.001 |
| benchmark | bpic2017_accepted | 0.1000 | 0.886 ± 0.005 | 0.7820 | 0.9570 | 0.838 ± 0.013 | 0.0000 | 0.1620 | 0.864 ± 0.004 |
| benchmark | bpic2017_accepted | 0.2000 | 0.812 ± 0.002 | 0.6180 | 0.9430 | 0.986 ± 0.005 | 0.0140 | 0.0000 | 0.824 ± 0.001 |
| benchmark | bpic2017_cancelled | 0.0500 | 0.948 ± 0.000 | 0.9320 | 0.9630 | 0.597 ± 0.001 | 0.0000 | 0.4030 | 0.914 ± 0.001 |
| benchmark | bpic2017_cancelled | 0.1000 | 0.909 ± 0.005 | 0.8890 | 0.9280 | 0.686 ± 0.011 | 0.0000 | 0.3140 | 0.868 ± 0.005 |
| benchmark | bpic2017_cancelled | 0.2000 | 0.808 ± 0.007 | 0.8590 | 0.7640 | 0.894 ± 0.013 | 0.0000 | 0.1060 | 0.786 ± 0.005 |
| benchmark | bpic2017_refused | 0.0500 | 0.966 ± 0.003 | 0.7370 | 1.0000 | 0.697 ± 0.025 | 0.0000 | 0.3030 | 0.952 ± 0.003 |
| benchmark | bpic2017_refused | 0.1000 | 0.916 ± 0.001 | 0.4230 | 0.9880 | 0.995 ± 0.002 | 0.0000 | 0.0050 | 0.915 ± 0.000 |
| benchmark | bpic2017_refused | 0.2000 | 0.803 ± 0.006 | 0.0140 | 0.9180 | 0.861 ± 0.007 | 0.1390 | 0.0000 | 0.933 ± 0.001 |
| benchmark | sepsis_cases_1 | 0.0500 | 0.957 ± 0.031 | 0.6180 | 0.9980 | 0.298 ± 0.201 | 0.0000 | 0.7020 | 0.858 ± 0.016 |
| benchmark | sepsis_cases_1 | 0.1000 | 0.934 ± 0.041 | 0.4310 | 0.9950 | 0.516 ± 0.303 | 0.0000 | 0.4840 | 0.872 ± 0.016 |
| benchmark | sepsis_cases_1 | 0.2000 | 0.710 ± 0.107 | 0.0100 | 0.7950 | 0.809 ± 0.111 | 0.1910 | 0.0000 | 0.877 ± 0.018 |
| benchmark | sepsis_cases_2 | 0.0500 | 0.865 ± 0.035 | 0.5210 | 0.9040 | 0.951 ± 0.022 | 0.0460 | 0.0040 | 0.906 ± 0.028 |
| benchmark | sepsis_cases_2 | 0.1000 | 0.806 ± 0.049 | 0.4750 | 0.8430 | 0.869 ± 0.043 | 0.1310 | 0.0000 | 0.927 ± 0.029 |
| benchmark | sepsis_cases_2 | 0.2000 | 0.710 ± 0.046 | 0.4330 | 0.7420 | 0.750 ± 0.044 | 0.2500 | 0.0000 | 0.947 ± 0.026 |
| benchmark | sepsis_cases_3 | 0.0500 | 0.963 ± 0.012 | 0.9950 | 0.8230 | 0.364 ± 0.071 | 0.0000 | 0.6360 | 0.900 ± 0.017 |
| benchmark | sepsis_cases_3 | 0.1000 | 0.928 ± 0.008 | 0.9890 | 0.6650 | 0.602 ± 0.031 | 0.0000 | 0.3980 | 0.881 ± 0.009 |
| benchmark | sepsis_cases_3 | 0.2000 | 0.775 ± 0.028 | 0.8950 | 0.2520 | 0.917 ± 0.037 | 0.0830 | 0.0000 | 0.845 ± 0.007 |
| benchmark | traffic_fines_1 | 0.0500 | 0.897 ± 0.027 | 0.9910 | 0.8140 | 0.570 ± 0.091 | 0.0000 | 0.4300 | 0.823 ± 0.022 |
| benchmark | traffic_fines_1 | 0.1000 | 0.840 ± 0.011 | 0.9890 | 0.7070 | 0.728 ± 0.018 | 0.0000 | 0.2720 | 0.780 ± 0.011 |
| benchmark | traffic_fines_1 | 0.2000 | 0.779 ± 0.015 | 0.9840 | 0.5950 | 0.836 ± 0.027 | 0.0000 | 0.1640 | 0.736 ± 0.010 |
| strict | bpic2012_accepted | 0.0500 | 0.941 ± 0.004 | 0.9280 | 0.9550 | 0.174 ± 0.008 | 0.0000 | 0.8260 | 0.659 ± 0.023 |
| strict | bpic2012_accepted | 0.1000 | 0.895 ± 0.006 | 0.8690 | 0.9230 | 0.276 ± 0.013 | 0.0000 | 0.7240 | 0.619 ± 0.022 |
| strict | bpic2012_accepted | 0.2000 | 0.798 ± 0.010 | 0.7530 | 0.8470 | 0.478 ± 0.008 | 0.0000 | 0.5220 | 0.577 ± 0.015 |
| strict | bpic2017_accepted | 0.0500 | 0.941 ± 0.001 | 0.9020 | 0.9670 | 0.283 ± 0.005 | 0.0000 | 0.7170 | 0.790 ± 0.002 |
| strict | bpic2017_accepted | 0.1000 | 0.888 ± 0.001 | 0.8130 | 0.9400 | 0.434 ± 0.002 | 0.0000 | 0.5660 | 0.741 ± 0.001 |
| strict | bpic2017_accepted | 0.2000 | 0.791 ± 0.002 | 0.6200 | 0.9100 | 0.684 ± 0.002 | 0.0000 | 0.3160 | 0.694 ± 0.002 |
| strict | sepsis_cases_1 | 0.0500 | 0.962 ± 0.016 | 0.6580 | 0.9990 | 0.336 ± 0.165 | 0.0000 | 0.6640 | 0.869 ± 0.046 |
| strict | sepsis_cases_1 | 0.1000 | 0.922 ± 0.037 | 0.3190 | 0.9960 | 0.661 ± 0.341 | 0.0000 | 0.3390 | 0.865 ± 0.043 |
| strict | sepsis_cases_1 | 0.2000 | 0.786 ± 0.054 | 0.0100 | 0.8810 | 0.897 ± 0.062 | 0.1030 | 0.0000 | 0.877 ± 0.024 |
| strict | traffic_fines_1 | 0.0500 | 0.900 ± 0.016 | 0.9890 | 0.8340 | 0.522 ± 0.037 | 0.0000 | 0.4780 | 0.809 ± 0.018 |
| strict | traffic_fines_1 | 0.1000 | 0.884 ± 0.028 | 0.9770 | 0.8160 | 0.561 ± 0.065 | 0.0000 | 0.4390 | 0.796 ± 0.027 |
| strict | traffic_fines_1 | 0.2000 | 0.779 ± 0.004 | 0.8340 | 0.7390 | 0.849 ± 0.006 | 0.0000 | 0.1510 | 0.740 ± 0.005 |


## 8. Governance: confidence-threshold deferral and risk–coverage

τ on confidence max(p, 1 − p) is set on validation part B to reach the target coverage and applied to test. `n_unique_conf_values_test` shows how many distinct confidence values exist (isotonic/Venn–Abers plateaus make exact coverage targets unreachable).

| protocol | task | model | target_coverage | realized_coverage_mean | acc_automated_mean | auc_automated_mean | n_unique_conf_values_test_mean |
|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | LGBM (raw) | 0.700 | 0.796 | 0.644 | 0.730 | 15157.000 |
| benchmark | bpic2012_accepted | LGBM (raw) | 0.800 | 0.869 | 0.633 | 0.718 | 15157.000 |
| benchmark | bpic2012_accepted | LGBM (raw) | 0.900 | 0.935 | 0.624 | 0.708 | 15157.000 |
| benchmark | bpic2012_accepted | Stack (proposed) | 0.700 | 0.801 | 0.656 | 0.739 | 30637.000 |
| benchmark | bpic2012_accepted | Stack (proposed) | 0.800 | 0.869 | 0.645 | 0.726 | 30637.000 |
| benchmark | bpic2012_accepted | Stack (proposed) | 0.900 | 0.932 | 0.635 | 0.716 | 30637.000 |
| benchmark | bpic2012_cancelled | LGBM (raw) | 0.700 | 0.725 | 0.818 | 0.744 | 4357.400 |
| benchmark | bpic2012_cancelled | LGBM (raw) | 0.800 | 0.805 | 0.805 | 0.732 | 4357.400 |
| benchmark | bpic2012_cancelled | LGBM (raw) | 0.900 | 0.884 | 0.794 | 0.721 | 4357.400 |
| benchmark | bpic2012_cancelled | Stack (proposed) | 0.700 | 0.738 | 0.818 | 0.765 | 30635.200 |
| benchmark | bpic2012_cancelled | Stack (proposed) | 0.800 | 0.816 | 0.806 | 0.748 | 30635.200 |
| benchmark | bpic2012_cancelled | Stack (proposed) | 0.900 | 0.899 | 0.796 | 0.732 | 30635.200 |
| benchmark | bpic2012_declined | LGBM (raw) | 0.700 | 0.729 | 0.830 | 0.574 | 3795.400 |
| benchmark | bpic2012_declined | LGBM (raw) | 0.800 | 0.835 | 0.827 | 0.569 | 3795.400 |
| benchmark | bpic2012_declined | LGBM (raw) | 0.900 | 0.912 | 0.824 | 0.572 | 3795.400 |
| benchmark | bpic2012_declined | Stack (proposed) | 0.700 | 0.746 | 0.835 | 0.593 | 30636.400 |
| benchmark | bpic2012_declined | Stack (proposed) | 0.800 | 0.846 | 0.830 | 0.589 | 30636.400 |
| benchmark | bpic2012_declined | Stack (proposed) | 0.900 | 0.924 | 0.827 | 0.588 | 30636.400 |
| benchmark | bpic2017_accepted | LGBM (raw) | 0.700 | 0.736 | 0.899 | 0.953 | 7255.800 |
| benchmark | bpic2017_accepted | LGBM (raw) | 0.800 | 0.856 | 0.860 | 0.929 | 7255.800 |
| benchmark | bpic2017_accepted | LGBM (raw) | 0.900 | 0.945 | 0.834 | 0.910 | 7255.800 |
| benchmark | bpic2017_accepted | Stack (proposed) | 0.700 | 0.733 | 0.900 | 0.955 | 124809.800 |
| benchmark | bpic2017_accepted | Stack (proposed) | 0.800 | 0.850 | 0.861 | 0.932 | 124809.800 |
| benchmark | bpic2017_accepted | Stack (proposed) | 0.900 | 0.936 | 0.837 | 0.913 | 124809.800 |
| benchmark | bpic2017_cancelled | LGBM (raw) | 0.700 | 0.705 | 0.856 | 0.929 | 6318.600 |
| benchmark | bpic2017_cancelled | LGBM (raw) | 0.800 | 0.796 | 0.819 | 0.909 | 6318.600 |
| benchmark | bpic2017_cancelled | LGBM (raw) | 0.900 | 0.898 | 0.784 | 0.886 | 6318.600 |
| benchmark | bpic2017_cancelled | Stack (proposed) | 0.700 | 0.694 | 0.864 | 0.931 | 124799.200 |
| benchmark | bpic2017_cancelled | Stack (proposed) | 0.800 | 0.800 | 0.817 | 0.908 | 124799.200 |
| benchmark | bpic2017_cancelled | Stack (proposed) | 0.900 | 0.898 | 0.784 | 0.886 | 124799.200 |
| benchmark | bpic2017_refused | LGBM (raw) | 0.700 | 0.684 | 0.954 | 0.776 | 817.600 |
| benchmark | bpic2017_refused | LGBM (raw) | 0.800 | 0.772 | 0.943 | 0.765 | 817.600 |
| benchmark | bpic2017_refused | LGBM (raw) | 0.900 | 0.893 | 0.929 | 0.754 | 817.600 |
| benchmark | bpic2017_refused | Stack (proposed) | 0.700 | 0.659 | 0.956 | 0.776 | 111599.200 |
| benchmark | bpic2017_refused | Stack (proposed) | 0.800 | 0.786 | 0.942 | 0.758 | 111599.200 |
| benchmark | bpic2017_refused | Stack (proposed) | 0.900 | 0.891 | 0.929 | 0.768 | 111599.200 |
| benchmark | sepsis_cases_1 | LGBM (raw) | 0.700 | 0.674 | 0.874 | 0.354 | 114.600 |
| benchmark | sepsis_cases_1 | LGBM (raw) | 0.800 | 0.732 | 0.877 | 0.363 | 114.600 |
| benchmark | sepsis_cases_1 | LGBM (raw) | 0.900 | 0.820 | 0.880 | 0.376 | 114.600 |
| benchmark | sepsis_cases_1 | Stack (proposed) | 0.700 | 0.459 | 0.865 | 0.433 | 2023.200 |
| benchmark | sepsis_cases_1 | Stack (proposed) | 0.800 | 0.588 | 0.870 | 0.436 | 2023.200 |
| benchmark | sepsis_cases_1 | Stack (proposed) | 0.900 | 0.732 | 0.872 | 0.452 | 2023.200 |
| benchmark | sepsis_cases_2 | LGBM (raw) | 0.700 | 0.698 | 0.967 | 0.500 | 605.400 |
| benchmark | sepsis_cases_2 | LGBM (raw) | 0.800 | 0.771 | 0.963 | 0.535 | 605.400 |
| benchmark | sepsis_cases_2 | LGBM (raw) | 0.900 | 0.851 | 0.958 | 0.593 | 605.400 |
| benchmark | sepsis_cases_2 | Stack (proposed) | 0.700 | 0.644 | 0.953 | 0.882 | 1859.000 |
| benchmark | sepsis_cases_2 | Stack (proposed) | 0.800 | 0.747 | 0.947 | 0.860 | 1859.000 |
| benchmark | sepsis_cases_2 | Stack (proposed) | 0.900 | 0.843 | 0.932 | 0.852 | 1859.000 |
| benchmark | sepsis_cases_3 | LGBM (raw) | 0.700 | 0.644 | 0.866 | 0.493 | 653.400 |
| benchmark | sepsis_cases_3 | LGBM (raw) | 0.800 | 0.730 | 0.861 | 0.518 | 653.400 |
| benchmark | sepsis_cases_3 | LGBM (raw) | 0.900 | 0.848 | 0.848 | 0.565 | 653.400 |
| benchmark | sepsis_cases_3 | Stack (proposed) | 0.700 | 0.587 | 0.884 | 0.640 | 2259.000 |
| benchmark | sepsis_cases_3 | Stack (proposed) | 0.800 | 0.671 | 0.872 | 0.656 | 2259.000 |
| benchmark | sepsis_cases_3 | Stack (proposed) | 0.900 | 0.794 | 0.864 | 0.667 | 2259.000 |
| benchmark | traffic_fines_1 | LGBM (raw) | 0.700 | 0.713 | 0.788 | 0.804 | 12623.400 |
| benchmark | traffic_fines_1 | LGBM (raw) | 0.800 | 0.791 | 0.752 | 0.804 | 12623.400 |
| benchmark | traffic_fines_1 | LGBM (raw) | 0.900 | 0.867 | 0.725 | 0.800 | 12623.400 |
| benchmark | traffic_fines_1 | Stack (proposed) | 0.700 | 0.780 | 0.760 | 0.810 | 16450.400 |
| benchmark | traffic_fines_1 | Stack (proposed) | 0.800 | 0.827 | 0.741 | 0.809 | 16450.400 |
| benchmark | traffic_fines_1 | Stack (proposed) | 0.900 | 0.929 | 0.707 | 0.800 | 16450.400 |
| strict | bpic2012_accepted | LGBM (raw) | 0.700 | 0.709 | 0.548 | 0.586 | 8736.400 |
| strict | bpic2012_accepted | LGBM (raw) | 0.800 | 0.808 | 0.543 | 0.579 | 8736.400 |
| strict | bpic2012_accepted | LGBM (raw) | 0.900 | 0.906 | 0.537 | 0.574 | 8736.400 |
| strict | bpic2012_accepted | Stack (proposed) | 0.700 | 0.683 | 0.558 | 0.593 | 17702.000 |
| strict | bpic2012_accepted | Stack (proposed) | 0.800 | 0.786 | 0.551 | 0.585 | 17702.000 |
| strict | bpic2012_accepted | Stack (proposed) | 0.900 | 0.892 | 0.545 | 0.577 | 17702.000 |
| strict | bpic2017_accepted | LGBM (raw) | 0.700 | 0.723 | 0.687 | 0.706 | 55095.000 |
| strict | bpic2017_accepted | LGBM (raw) | 0.800 | 0.813 | 0.675 | 0.698 | 55095.000 |
| strict | bpic2017_accepted | LGBM (raw) | 0.900 | 0.911 | 0.661 | 0.688 | 55095.000 |
| strict | bpic2017_accepted | Stack (proposed) | 0.700 | 0.722 | 0.689 | 0.710 | 121327.000 |
| strict | bpic2017_accepted | Stack (proposed) | 0.800 | 0.819 | 0.675 | 0.698 | 121327.000 |
| strict | bpic2017_accepted | Stack (proposed) | 0.900 | 0.912 | 0.663 | 0.688 | 121327.000 |
| strict | sepsis_cases_1 | LGBM (raw) | 0.700 | 0.583 | 0.868 | 0.409 | 282.600 |
| strict | sepsis_cases_1 | LGBM (raw) | 0.800 | 0.703 | 0.871 | 0.423 | 282.600 |
| strict | sepsis_cases_1 | LGBM (raw) | 0.900 | 0.840 | 0.886 | 0.378 | 282.600 |
| strict | sepsis_cases_1 | Stack (proposed) | 0.700 | 0.713 | 0.887 | 0.504 | 1893.800 |
| strict | sepsis_cases_1 | Stack (proposed) | 0.800 | 0.796 | 0.885 | 0.508 | 1893.800 |
| strict | sepsis_cases_1 | Stack (proposed) | 0.900 | 0.881 | 0.881 | 0.504 | 1893.800 |
| strict | traffic_fines_1 | LGBM (raw) | 0.700 | 0.783 | 0.738 | 0.790 | 8821.600 |
| strict | traffic_fines_1 | LGBM (raw) | 0.800 | 0.852 | 0.725 | 0.787 | 8821.600 |
| strict | traffic_fines_1 | LGBM (raw) | 0.900 | 0.925 | 0.717 | 0.782 | 8821.600 |
| strict | traffic_fines_1 | Stack (proposed) | 0.700 | 0.687 | 0.770 | 0.835 | 39930.000 |
| strict | traffic_fines_1 | Stack (proposed) | 0.800 | 0.817 | 0.745 | 0.816 | 39930.000 |
| strict | traffic_fines_1 | Stack (proposed) | 0.900 | 0.914 | 0.729 | 0.802 | 39930.000 |


Area under the risk–coverage curve (mean error rate over coverage 0.05..1.00; lower is better; seed 0):

| protocol | task | LGBM | LR | Stack (proposed) | Transformer |
|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | 0.2569 | 0.2992 | 0.2435 | 0.2595 |
| benchmark | bpic2012_cancelled | 0.1315 | 0.1331 | 0.1238 | 0.1317 |
| benchmark | bpic2012_declined | 0.1446 | 0.1701 | 0.1371 | 0.1460 |
| benchmark | bpic2017_accepted | 0.0642 | 0.2420 | 0.0635 | 0.0770 |
| benchmark | bpic2017_cancelled | 0.1018 | 0.4048 | 0.1012 | 0.1575 |
| benchmark | bpic2017_refused | 0.0352 | 0.0910 | 0.0323 | 0.0546 |
| benchmark | sepsis_cases_1 | 0.1451 | 0.0990 | 0.1712 | 0.1477 |
| benchmark | sepsis_cases_2 | 0.0334 | 0.0181 | 0.0702 | 0.0336 |
| benchmark | sepsis_cases_3 | 0.1357 | 0.1162 | 0.1172 | 0.1081 |
| benchmark | traffic_fines_1 | 0.1619 | 0.1495 | 0.1542 | 0.1613 |
| strict | bpic2012_accepted | 0.4097 | 0.4609 | 0.4257 | 0.4298 |
| strict | bpic2017_accepted | 0.2565 | 0.3840 | 0.2534 | 0.2650 |
| strict | sepsis_cases_1 | 0.1528 | 0.0942 | 0.1026 | 0.1422 |
| strict | traffic_fines_1 | 0.1782 | 0.3082 | 0.1664 | 0.1760 |


## 9. Cost-based decisioning

One decision per test case at a fixed prefix length (BPIC 5, Sepsis 5, Traffic 2). Intervene iff q = P(adverse) > r, r = C/B. Net benefit per case (units of B) = Σ_intervened (1[adverse] − r) / n; assumes the intervention fully prevents the adverse outcome (stylised). Adverse outcome: accepted tasks → not accepted; declined/cancelled/refused → that outcome; sepsis 1/2 → return ER / ICU admission; sepsis 3 → NOT released with type A; traffic → credit collection. Mean over 5 seeds.


### r = 0.2

| protocol | task | Best tuned GBM + isotonic q>r | LGBM raw q>r | LR q>r | LSTM q>r | Stack (proposed) fixed 0.5 threshold | Stack (proposed) q>r | Transformer q>r | always intervene | never intervene | oracle |
|---|---|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | 0.2856 | 0.2856 | 0.2850 | 0.2856 | 0.2160 | 0.2856 | 0.2856 | 0.2856 | 0.0000 | 0.3885 |
| benchmark | bpic2012_cancelled | 0.0924 | 0.0924 | 0.0920 | 0.0928 | 0.0003 | 0.0924 | 0.0924 | 0.0924 | 0.0000 | 0.2339 |
| benchmark | bpic2012_declined | 0.0056 | 0.0060 | -0.0137 | -0.0080 | 0.0000 | 0.0059 | 0.0015 | -0.0068 | 0.0000 | 0.1545 |
| benchmark | bpic2017_accepted | 0.3991 | 0.3991 | 0.3896 | 0.3983 | 0.3839 | 0.3991 | 0.3991 | 0.3991 | 0.0000 | 0.4793 |
| benchmark | bpic2017_cancelled | 0.2716 | 0.2716 | 0.2707 | 0.2689 | 0.1744 | 0.2716 | 0.2715 | 0.2716 | 0.0000 | 0.3773 |
| benchmark | bpic2017_refused | 0.0038 | 0.0000 | -0.0007 | -0.0014 | 0.0000 | 0.0004 | 0.0030 | -0.0725 | 0.0000 | 0.1020 |
| benchmark | sepsis_cases_1 | -0.0390 | -0.0020 | -0.0166 | -0.0247 | -0.0033 | -0.0479 | -0.0283 | -0.0854 | 0.0000 | 0.0917 |
| benchmark | sepsis_cases_2 | 0.0444 | 0.0595 | 0.0654 | 0.0441 | 0.0538 | 0.0459 | 0.0500 | -0.0654 | 0.0000 | 0.1077 |
| benchmark | sepsis_cases_3 | 0.0186 | 0.0166 | 0.0229 | 0.0033 | 0.0158 | 0.0217 | 0.0112 | -0.0471 | 0.0000 | 0.1223 |
| benchmark | traffic_fines_1 | 0.2839 | 0.2668 | 0.2840 | 0.2832 | 0.2839 | 0.2839 | 0.2838 | 0.1985 | 0.0000 | 0.3188 |
| strict | bpic2012_accepted | 0.2859 | 0.2856 | 0.2856 | 0.2856 | 0.1930 | 0.2856 | 0.2856 | 0.2856 | 0.0000 | 0.3885 |
| strict | bpic2017_accepted | 0.3991 | 0.3991 | 0.3989 | 0.3991 | 0.3782 | 0.3991 | 0.3990 | 0.3991 | 0.0000 | 0.4793 |
| strict | sepsis_cases_1 | -0.0586 | -0.0140 | -0.0191 | -0.0041 | -0.0025 | -0.0469 | -0.0183 | -0.0854 | 0.0000 | 0.0917 |
| strict | traffic_fines_1 | 0.2085 | 0.1796 | 0.2085 | 0.2085 | 0.2082 | 0.2084 | 0.2084 | 0.1364 | 0.0000 | 0.2691 |


### r = 0.5

| protocol | task | Best tuned GBM + isotonic q>r | LGBM raw q>r | LR q>r | LSTM q>r | Stack (proposed) fixed 0.5 threshold | Stack (proposed) q>r | Transformer q>r | always intervene | never intervene | oracle |
|---|---|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | 0.0050 | -0.0050 | -0.0096 | -0.0124 | 0.0094 | 0.0094 | -0.0037 | -0.0144 | 0.0000 | 0.2428 |
| benchmark | bpic2012_cancelled | -0.0032 | -0.0012 | -0.0005 | -0.0001 | -0.0006 | -0.0006 | 0.0002 | -0.2076 | 0.0000 | 0.1462 |
| benchmark | bpic2012_declined | 0.0002 | -0.0012 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.3068 | 0.0000 | 0.0966 |
| benchmark | bpic2017_accepted | 0.1106 | 0.1117 | 0.1117 | 0.1077 | 0.1117 | 0.1117 | 0.1116 | 0.0991 | 0.0000 | 0.2995 |
| benchmark | bpic2017_cancelled | 0.0048 | 0.0062 | -0.0010 | 0.0026 | 0.0058 | 0.0058 | 0.0015 | -0.0284 | 0.0000 | 0.2358 |
| benchmark | bpic2017_refused | 0.0000 | 0.0000 | -0.0001 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.3725 | 0.0000 | 0.0637 |
| benchmark | sepsis_cases_1 | -0.0185 | 0.0000 | 0.0000 | 0.0000 | -0.0121 | -0.0121 | 0.0000 | -0.3854 | 0.0000 | 0.0573 |
| benchmark | sepsis_cases_2 | 0.0038 | 0.0167 | 0.0353 | 0.0045 | 0.0058 | 0.0058 | 0.0128 | -0.3654 | 0.0000 | 0.0673 |
| benchmark | sepsis_cases_3 | -0.0102 | -0.0013 | 0.0000 | 0.0000 | -0.0025 | -0.0025 | 0.0000 | -0.3471 | 0.0000 | 0.0764 |
| benchmark | traffic_fines_1 | 0.1126 | 0.1121 | 0.1125 | 0.1112 | 0.1126 | 0.1126 | 0.1125 | -0.1015 | 0.0000 | 0.1993 |
| strict | bpic2012_accepted | -0.0029 | 0.0046 | -0.0224 | -0.0067 | 0.0049 | 0.0049 | -0.0050 | -0.0144 | 0.0000 | 0.2428 |
| strict | bpic2017_accepted | 0.1104 | 0.1115 | 0.1004 | 0.1028 | 0.1112 | 0.1112 | 0.1036 | 0.0991 | 0.0000 | 0.2995 |
| strict | sepsis_cases_1 | -0.0038 | -0.0006 | 0.0000 | 0.0000 | -0.0102 | -0.0102 | 0.0000 | -0.3854 | 0.0000 | 0.0573 |
| strict | traffic_fines_1 | 0.0170 | 0.0157 | 0.0157 | 0.0147 | 0.0173 | 0.0173 | 0.0151 | -0.1636 | 0.0000 | 0.1682 |


### r = 0.8

| protocol | task | Best tuned GBM + isotonic q>r | LGBM raw q>r | LR q>r | LSTM q>r | Stack (proposed) fixed 0.5 threshold | Stack (proposed) q>r | Transformer q>r | always intervene | never intervene | oracle |
|---|---|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | 0.0001 | 0.0002 | -0.0009 | 0.0000 | -0.1972 | -0.0001 | 0.0000 | -0.3144 | 0.0000 | 0.0971 |
| benchmark | bpic2012_cancelled | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.0015 | 0.0000 | 0.0000 | -0.5076 | 0.0000 | 0.0585 |
| benchmark | bpic2012_declined | -0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.6068 | 0.0000 | 0.0386 |
| benchmark | bpic2017_accepted | -0.0006 | -0.0000 | -0.0159 | -0.0001 | -0.1605 | -0.0000 | 0.0000 | -0.2009 | 0.0000 | 0.1198 |
| benchmark | bpic2017_cancelled | 0.0000 | 0.0000 | -0.0277 | 0.0000 | -0.1627 | 0.0000 | 0.0000 | -0.3284 | 0.0000 | 0.0943 |
| benchmark | bpic2017_refused | 0.0000 | 0.0000 | -0.0001 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.6725 | 0.0000 | 0.0255 |
| benchmark | sepsis_cases_1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.0209 | 0.0000 | 0.0000 | -0.6854 | 0.0000 | 0.0229 |
| benchmark | sepsis_cases_2 | -0.0082 | 0.0000 | 0.0115 | 0.0000 | -0.0423 | -0.0079 | 0.0015 | -0.6654 | 0.0000 | 0.0269 |
| benchmark | sepsis_cases_3 | -0.0071 | 0.0000 | 0.0000 | 0.0000 | -0.0209 | -0.0054 | 0.0000 | -0.6471 | 0.0000 | 0.0306 |
| benchmark | traffic_fines_1 | -0.0009 | -0.0144 | -0.0036 | -0.0002 | -0.0587 | -0.0004 | -0.0007 | -0.4015 | 0.0000 | 0.0797 |
| strict | bpic2012_accepted | -0.0037 | -0.0003 | -0.0013 | 0.0000 | -0.1832 | -0.0020 | 0.0000 | -0.3144 | 0.0000 | 0.0971 |
| strict | bpic2017_accepted | -0.0000 | 0.0002 | -0.0145 | -0.0002 | -0.1557 | -0.0001 | 0.0001 | -0.2009 | 0.0000 | 0.1198 |
| strict | sepsis_cases_1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.0178 | -0.0010 | 0.0000 | -0.6854 | 0.0000 | 0.0229 |
| strict | traffic_fines_1 | -0.0000 | -0.0078 | -0.0921 | -0.0001 | -0.1736 | 0.0000 | -0.0000 | -0.4636 | 0.0000 | 0.0673 |


Headline over all tasks × cost ratios r ∈ {0.05, …, 0.95} (19 values):

| protocol | n | share_proposed_ge_best_trivial | mean_gain_vs_trivial | median_frac_of_oracle_gap | share_proposed_ge_fixed05 | mean_gain_vs_fixed05 | share_proposed_ge_LGBMraw |
|---|---|---|---|---|---|---|---|
| benchmark | 190 | 0.6737 | 0.0070 | 0.0000 | 0.8053 | 0.0380 | 0.6737 |
| strict | 76 | 0.5658 | 0.0061 | 0.0000 | 0.8553 | 0.0603 | 0.6579 |


## 10. Explanation quality (proposed ensemble, tree part)

SHAP: exact additive attribution of the stack log-odds tree part, φ_j = Σ_m w_m φ_mj (TreeSHAP of LightGBM, XGBoost, CatBoost in log-odds; w_m = meta weights), Transformer term held fixed per instance; additivity error reported in `per_task/*/*/xai_info.json`. LIME (1,000 samples, top-10) explains the same function. 100 stratified test prefixes per task (BENCHMARK representative tasks), LIME stability on 30. Deletion: features supporting the predicted class are removed (aggregation features → training mean, index features → missing).

| metric | bpic2012_accepted | bpic2017_accepted | sepsis_cases_2 | traffic_fines_1 |
|---|---|---|---|---|
| Perturbed continuous features (count) | 20.0000 | 34.0000 | 31.0000 | 15.0000 |
| Runtime LIME 1000 samples (s/instance) | 0.1665 | 0.2343 | 0.2238 | 0.1820 |
| Runtime ensemble TreeSHAP (s/instance) | 0.0193 | 0.0184 | 0.0196 | 0.0166 |
| SHAP-LIME agreement: Jaccard top-5 | 0.1250 ± 0.0417 | 0.5097 ± 0.1465 | 0.1371 ± 0.0738 | 0.2893 ± 0.1796 |
| SHAP-LIME agreement: Kendall tau on |attr| of LIME top-10 | 0.3985 ± 0.1344 | 0.7039 ± 0.0903 | 0.5608 ± 0.1100 | 0.6223 ± 0.0601 |
| SHAP-LIME sign agreement on shared top-5 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 |
| SHAP-LIME(no discretization) agreement: Jaccard top-5 | 0.2818 ± 0.1667 | 0.4536 ± 0.2890 | 0.2236 ± 0.1436 | 0.5988 ± 0.1386 |
| Stability LIME: Jaccard top-5 across LIME sampling seeds (3) | 0.9778 ± 0.0831 | 0.6767 ± 0.0889 | 0.4821 ± 0.0818 | 0.2967 ± 0.0830 |
| Stability LIME: Jaccard top-5 under perturbation (3 reps) | 0.9519 ± 0.0893 | 0.8032 ± 0.1197 | 0.5481 ± 0.1103 | 0.5073 ± 0.1306 |
| Stability SHAP: Jaccard top-5 across 5 training seeds (pairwise) | 0.5795 ± 0.1155 | 0.6047 ± 0.0979 | 0.4316 ± 0.1222 | 0.8363 ± 0.1083 |
| Stability SHAP: Jaccard top-5 under perturbation (10 reps) | 0.9833 ± 0.0426 | 0.8940 ± 0.0741 | 0.9240 ± 0.0882 | 0.9487 ± 0.0948 |


Deletion: mean drop in predicted-class probability

| task | k | LIME | LIME (no discretization) | SHAP | random |
|---|---|---|---|---|---|
| bpic2012_accepted | 1 | 0.0479 | 0.0456 | 0.0835 | 0.0009 |
| bpic2012_accepted | 2 | 0.1694 | 0.0384 | 0.1285 | 0.0028 |
| bpic2012_accepted | 3 | 0.2044 | 0.0543 | 0.1571 | 0.0039 |
| bpic2012_accepted | 5 | 0.2799 | 0.0649 | 0.2037 | 0.0053 |
| bpic2012_accepted | 7 | 0.2891 | 0.0688 | 0.2494 | 0.0081 |
| bpic2012_accepted | 10 | 0.2897 | 0.0702 | 0.3050 | 0.0109 |
| bpic2012_accepted | 15 | 0.2897 | 0.0702 | 0.3572 | 0.0187 |
| bpic2012_accepted | 20 | 0.2897 | 0.0702 | 0.3716 | 0.0243 |
| bpic2017_accepted | 1 | 0.2717 | -0.0959 | 0.2546 | -0.0009 |
| bpic2017_accepted | 2 | 0.3511 | -0.0924 | 0.4169 | 0.0009 |
| bpic2017_accepted | 3 | 0.4141 | -0.0923 | 0.4416 | 0.0003 |
| bpic2017_accepted | 5 | 0.4361 | -0.0837 | 0.4955 | 0.0020 |
| bpic2017_accepted | 7 | 0.4362 | -0.0838 | 0.5046 | 0.0001 |
| bpic2017_accepted | 10 | 0.4362 | -0.0858 | 0.5160 | 0.0043 |
| bpic2017_accepted | 15 | 0.4362 | -0.0858 | 0.5500 | 0.0097 |
| bpic2017_accepted | 20 | 0.4362 | -0.0858 | 0.5718 | 0.0105 |
| sepsis_cases_2 | 1 | 0.0398 | 0.0796 | 0.1705 | 0.0013 |
| sepsis_cases_2 | 2 | 0.0524 | 0.0868 | 0.1911 | 0.0028 |
| sepsis_cases_2 | 3 | 0.0528 | 0.0984 | 0.1591 | 0.0038 |
| sepsis_cases_2 | 5 | 0.0540 | 0.1156 | 0.1690 | 0.0044 |
| sepsis_cases_2 | 7 | 0.0555 | 0.1142 | 0.1854 | 0.0072 |
| sepsis_cases_2 | 10 | 0.0570 | 0.1140 | 0.1868 | 0.0076 |
| sepsis_cases_2 | 15 | 0.0570 | 0.1140 | 0.1858 | 0.0100 |
| sepsis_cases_2 | 20 | 0.0570 | 0.1140 | 0.1771 | 0.0136 |
| traffic_fines_1 | 1 | 0.0000 | 0.0300 | 0.0464 | -0.0002 |
| traffic_fines_1 | 2 | 0.0112 | 0.0774 | 0.0582 | -0.0004 |
| traffic_fines_1 | 3 | 0.0238 | 0.0778 | 0.0590 | -0.0005 |
| traffic_fines_1 | 5 | 0.0400 | 0.0849 | 0.0756 | -0.0008 |
| traffic_fines_1 | 7 | 0.0400 | 0.0866 | 0.0791 | -0.0001 |
| traffic_fines_1 | 10 | 0.0400 | 0.0867 | 0.0936 | 0.0003 |
| traffic_fines_1 | 15 | 0.0400 | 0.0867 | 0.1034 | 0.0018 |
| traffic_fines_1 | 20 | 0.0400 | 0.0867 | 0.1059 | 0.0018 |


SHAP additivity check (max |Σφ + base − tree-part log-odds| over 2,000 test prefixes):

| protocol | task | additivity_max_abs_err | enc_LGBM | enc_XGB | enc_CatBoost |
|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | 0.00000184 | agg+index | agg | agg+index |
| benchmark | bpic2012_cancelled | 0.00000031 | agg | agg | agg |
| benchmark | bpic2012_declined | 0.00000013 | agg | agg+index | agg |
| benchmark | bpic2017_accepted | 0.00000002 | agg+index | agg | agg+index |
| benchmark | bpic2017_cancelled | 0.00000003 | agg | agg+index | agg+index |
| benchmark | bpic2017_refused | 0.00000097 | agg | agg+index | agg+index |
| benchmark | sepsis_cases_1 | 0.00000044 | agg+index | agg | agg |
| benchmark | sepsis_cases_2 | 0.00000165 | agg | agg+index | agg |
| benchmark | sepsis_cases_3 | 0.00000262 | agg+index | agg+index | agg |
| benchmark | traffic_fines_1 | 0.00000055 | agg+index | agg | agg+index |
| strict | bpic2012_accepted | 0.00000182 | agg+index | agg | agg+index |
| strict | bpic2017_accepted | 0.00000035 | agg+index | agg+index | agg+index |
| strict | sepsis_cases_1 | 0.00000010 | agg | agg+index | agg |
| strict | traffic_fines_1 | 0.00000035 | agg+index | agg | agg+index |


Global ensemble SHAP top-10 features (mean |φ|, 2,000 test prefixes, seed 0):

- **benchmark/bpic2012_accepted**: cnt_Activity=O_SENT_BACK-COMPLETE (0.462); static_AMOUNT_REQ (0.138); cnt_Activity=W_Valideren aanvraag-SCHEDULE (0.104); cnt_Activity=O_ACCEPTED-COMPLETE (0.082); cnt_Resource=11049 (0.063); cnt_Activity=A_CANCELLED-COMPLETE (0.061); open_cases_max (0.050); open_cases_min (0.043); cnt_Activity=W_Valideren aanvraag-START (0.040); timesincelastevent_sum (0.037)
- **benchmark/bpic2012_cancelled**: cnt_Activity=O_SENT_BACK-COMPLETE (0.539); open_cases_min (0.063); timesincelastevent_sum (0.058); cnt_Activity=A_CANCELLED-COMPLETE (0.052); timesincelastevent_max (0.045); open_cases_max (0.038); timesincemidnight_max (0.036); timesincelastevent_std (0.033); cnt_Resource=11049 (0.033); static_AMOUNT_REQ (0.033)
- **benchmark/bpic2012_declined**: static_AMOUNT_REQ (0.187); cnt_Activity=O_ACCEPTED-COMPLETE (0.084); cnt_Activity=A_DECLINED-COMPLETE (0.075); cnt_Activity=O_DECLINED-COMPLETE (0.061); timesincelastevent_max (0.053); open_cases_mean (0.049); month_max (0.046); cnt_Activity=A_CANCELLED-COMPLETE (0.044); timesincemidnight_max (0.043); cnt_Activity=A_APPROVED-COMPLETE (0.043)
- **benchmark/bpic2017_accepted**: cnt_Selected=False (0.889); CreditScore_mean (0.851); CreditScore_sum (0.411); cnt_Activity=O_Create Offer (0.265); static_ApplicationType=New credit (0.161); static_ApplicationType=Limit raise (0.127); cnt_Selected=True (0.119); CreditScore_max (0.112); CreditScore_std (0.101); cnt_Resource=User_1 (0.075)
- **benchmark/bpic2017_cancelled**: cnt_Selected=False (1.083); cnt_Selected=True (0.431); CreditScore_mean (0.207); cnt_Activity=O_Create Offer (0.145); CreditScore_max (0.124); MonthlyCost_max (0.108); static_ApplicationType=New credit (0.073); cnt_Resource=User_1 (0.069); CreditScore_sum (0.065); static_RequestedAmount (0.062)
- **benchmark/bpic2017_refused**: CreditScore_mean (0.670); cnt_Selected=True (0.413); CreditScore_sum (0.300); cnt_Accepted=True (0.267); CreditScore_std (0.168); MonthlyCost_max (0.127); CreditScore_max (0.117); static_ApplicationType=Limit raise (0.106); static_ApplicationType=New credit (0.089); NumberOfTerms_std (0.063)
- **benchmark/sepsis_cases_1**: weekday_mean (0.124); static_SIRSCritHeartRate=False (0.119); open_cases_min (0.099); static_DiagnosticECG=False (0.097); open_cases_mean (0.091); Leucocytes_max (0.079); static_DiagnosticXthorax=False (0.075); static_SIRSCritLeucos=False (0.074); timesincemidnight_mean (0.074); static_Diagnose=D (0.065)
- **benchmark/sepsis_cases_2**: static_Age (1.079); static_Diagnose=G (0.983); open_cases_max (0.514); static_SIRSCritTachypnea=False (0.416); weekday_mean (0.381); static_DiagnosticArtAstrup=False (0.358); static_Diagnose=other (0.345); static_Hypotensie=True (0.334); LacticAcid_max (0.246); timesincemidnight_mean (0.244)
- **benchmark/sepsis_cases_3**: static_Age (0.618); CRP_max (0.238); static_SIRSCritTemperature=True (0.214); timesincemidnight_max (0.181); LacticAcid_max (0.160); timesincemidnight_min (0.118); CRP_mean (0.095); open_cases_min (0.094); month_min (0.087); weekday_mean (0.087)
- **benchmark/traffic_fines_1**: cnt_Activity=Payment (0.556); cnt_Activity=Send Fine (0.351); idx_act_lag1 (0.295); cnt_lastSent=N (0.189); static_amount (0.149); cnt_Activity=Insert Date Appeal to Prefecture (0.065); expense_max (0.063); idx_tsl_lag1 (0.051); idx_act_lag2 (0.044); expense_std (0.029)
- **strict/bpic2012_accepted**: static_AMOUNT_REQ (0.144); month_max (0.061); cnt_Activity=O_SENT_BACK-COMPLETE (0.061); timesincemidnight_max (0.059); cnt_Activity=W_Afhandelen leads-SCHEDULE (0.055); timesincemidnight_min (0.051); timesincelastevent_max (0.049); weekday_mean (0.048); cnt_Activity=W_Completeren aanvraag-START (0.038); weekday_max (0.035)
- **strict/bpic2017_accepted**: cnt_Activity=O_Create Offer (0.283); cnt_Resource=User_1 (0.155); static_ApplicationType=New credit (0.105); static_RequestedAmount (0.078); FirstWithdrawalAmount_mean (0.068); month_mean (0.067); cnt_Action=Deleted (0.058); cnt_Activity=W_Handle leads (0.055); OfferedAmount_max (0.049); FirstWithdrawalAmount_max (0.042)
- **strict/sepsis_cases_1**: weekday_mean (0.095); static_Age (0.091); static_SIRSCritHeartRate=False (0.091); month_mean (0.091); hour_mean (0.065); static_Diagnose=other (0.063); timesincemidnight_max (0.054); month_max (0.053); cnt_Activity=IV Liquid (0.048); static_Diagnose=B (0.046)
- **strict/traffic_fines_1**: idx_act_lag1 (0.191); cnt_Activity=Payment (0.187); idx_act_lag3 (0.070); static_amount (0.056); expense_sum (0.055); cnt_notificationType=P (0.046); expense_std (0.039); cnt_lastSent=N (0.037); expense_max (0.033); idx_act_lag2 (0.031)


## 11. Ablation (mean ± sd over seeds; "untuned stack" uses 1 seed)

| protocol | task | variant | AUC | ECE | Brier | conf_cov | automation | nb_r03 | nb_r05 |
|---|---|---|---|---|---|---|---|---|---|
| benchmark | bpic2012_accepted | Best tuned GBM + isotonic | 0.6975 ± 0.0032 | 0.0371 ± 0.0040 | 0.2133 | 0.8900 | 0.4520 | 0.1856 | 0.0050 |
| benchmark | bpic2012_accepted | LGBM | 0.6975 ± 0.0030 | 0.0669 ± 0.0075 | 0.2166 | 0.8600 | 0.5190 | 0.1856 | -0.0050 |
| benchmark | bpic2012_accepted | Stack (proposed) | 0.7047 ± 0.0040 | 0.0459 ± 0.0019 | 0.2115 | 0.8640 | 0.5180 | 0.1856 | 0.0094 |
| benchmark | bpic2012_accepted | Stack of default GBMs (untuned) | 0.7026 | 0.0436 | 0.2113 | 0.8570 | 0.5290 | 0.1856 | 0.0091 |
| benchmark | bpic2012_accepted | Stack w/o Transformer | 0.7037 ± 0.0029 | 0.0450 ± 0.0025 | 0.2118 | 0.8630 | 0.5200 | 0.1856 | 0.0086 |
| benchmark | bpic2012_accepted | Stack w/o post-calibration | 0.7047 ± 0.0040 | 0.0459 ± 0.0019 | 0.2115 | 0.8640 | 0.5180 | 0.1856 | 0.0094 |
| benchmark | bpic2012_accepted | Transformer | 0.6823 ± 0.0061 | 0.0528 ± 0.0079 | 0.2206 | 0.8650 | 0.4910 | 0.1857 | -0.0037 |
| benchmark | bpic2012_cancelled | Best tuned GBM + isotonic | 0.7165 ± 0.0096 | 0.0454 ± 0.0050 | 0.1626 | 0.9260 | 0.4450 | -0.0049 | -0.0032 |
| benchmark | bpic2012_cancelled | LGBM | 0.7260 ± 0.0046 | 0.0978 ± 0.0139 | 0.1700 | 0.8870 | 0.5300 | -0.0055 | -0.0012 |
| benchmark | bpic2012_cancelled | Stack (proposed) | 0.7275 ± 0.0020 | 0.0481 ± 0.0035 | 0.1603 | 0.8910 | 0.5330 | -0.0047 | -0.0006 |
| benchmark | bpic2012_cancelled | Stack of default GBMs (untuned) | 0.7241 | 0.0494 | 0.1598 | 0.8720 | 0.5450 | -0.0076 | 0.0000 |
| benchmark | bpic2012_cancelled | Stack w/o Transformer | 0.7266 ± 0.0054 | 0.0473 ± 0.0026 | 0.1608 | 0.8910 | 0.5340 | -0.0011 | -0.0022 |
| benchmark | bpic2012_cancelled | Stack w/o post-calibration | 0.7275 ± 0.0020 | 0.0481 ± 0.0035 | 0.1603 | 0.8910 | 0.5330 | -0.0047 | -0.0006 |
| benchmark | bpic2012_cancelled | Transformer | 0.7143 ± 0.0033 | 0.0516 ± 0.0146 | 0.1661 | 0.8890 | 0.5160 | -0.0068 | 0.0002 |
| benchmark | bpic2012_declined | Best tuned GBM + isotonic | 0.5779 ± 0.0204 | 0.0465 ± 0.0124 | 0.1466 | 0.9460 | 0.1960 | -0.0000 | 0.0002 |
| benchmark | bpic2012_declined | LGBM | 0.5703 ± 0.0124 | 0.0466 ± 0.0052 | 0.1488 | 0.8900 | 0.3240 | -0.0056 | -0.0012 |
| benchmark | bpic2012_declined | Stack (proposed) | 0.5878 ± 0.0168 | 0.0394 ± 0.0051 | 0.1458 | 0.8980 | 0.3580 | -0.0027 | 0.0000 |
| benchmark | bpic2012_declined | Stack of default GBMs (untuned) | 0.5845 | 0.0370 | 0.1455 | 0.8910 | 0.3910 | -0.0035 | 0.0000 |
| benchmark | bpic2012_declined | Stack w/o Transformer | 0.5773 ± 0.0134 | 0.0372 ± 0.0074 | 0.1460 | 0.8820 | 0.3440 | -0.0031 | 0.0002 |
| benchmark | bpic2012_declined | Stack w/o post-calibration | 0.5878 ± 0.0168 | 0.0394 ± 0.0051 | 0.1458 | 0.8980 | 0.3580 | -0.0027 | 0.0000 |
| benchmark | bpic2012_declined | Transformer | 0.5740 ± 0.0148 | 0.0269 ± 0.0066 | 0.1485 | 0.9010 | 0.3390 | -0.0002 | 0.0000 |
| benchmark | bpic2017_accepted | Best tuned GBM + isotonic | 0.8984 ± 0.0004 | 0.0161 ± 0.0012 | 0.1201 | 0.9310 | 0.7030 | 0.2989 | 0.1106 |
| benchmark | bpic2017_accepted | LGBM | 0.8990 ± 0.0005 | 0.0303 ± 0.0133 | 0.1206 | 0.9030 | 0.7800 | 0.2987 | 0.1117 |
| benchmark | bpic2017_accepted | Stack (proposed) | 0.8993 ± 0.0003 | 0.0134 ± 0.0008 | 0.1195 | 0.9020 | 0.7790 | 0.2971 | 0.1117 |
| benchmark | bpic2017_accepted | Stack of default GBMs (untuned) | 0.8996 | 0.0108 | 0.1194 | 0.8980 | 0.7900 | 0.2974 | 0.1117 |
| benchmark | bpic2017_accepted | Stack w/o Transformer | 0.8993 ± 0.0004 | 0.0132 ± 0.0008 | 0.1194 | 0.9030 | 0.7770 | 0.2973 | 0.1117 |
| benchmark | bpic2017_accepted | Stack w/o post-calibration | 0.8993 ± 0.0003 | 0.0134 ± 0.0008 | 0.1195 | 0.9020 | 0.7790 | 0.2971 | 0.1117 |
| benchmark | bpic2017_accepted | Transformer | 0.8813 ± 0.0017 | 0.0250 ± 0.0089 | 0.1306 | 0.8940 | 0.7510 | 0.2985 | 0.1116 |
| benchmark | bpic2017_cancelled | Best tuned GBM + isotonic | 0.8611 ± 0.0010 | 0.0126 ± 0.0023 | 0.1451 | 0.9410 | 0.6130 | 0.1721 | 0.0048 |
| benchmark | bpic2017_cancelled | LGBM | 0.8636 ± 0.0007 | 0.0533 ± 0.0273 | 0.1494 | 0.9070 | 0.6860 | 0.1725 | 0.0062 |
| benchmark | bpic2017_cancelled | Stack (proposed) | 0.8638 ± 0.0006 | 0.0130 ± 0.0022 | 0.1446 | 0.9100 | 0.6820 | 0.1724 | 0.0058 |
| benchmark | bpic2017_cancelled | Stack of default GBMs (untuned) | 0.8641 | 0.0147 | 0.1445 | 0.9020 | 0.7020 | 0.1714 | 0.0041 |
| benchmark | bpic2017_cancelled | Stack w/o Transformer | 0.8637 ± 0.0007 | 0.0132 ± 0.0017 | 0.1445 | 0.9130 | 0.6750 | 0.1725 | 0.0060 |
| benchmark | bpic2017_cancelled | Stack w/o post-calibration | 0.8638 ± 0.0006 | 0.0130 ± 0.0022 | 0.1446 | 0.9100 | 0.6820 | 0.1724 | 0.0058 |
| benchmark | bpic2017_cancelled | Transformer | 0.7916 ± 0.0019 | 0.0312 ± 0.0096 | 0.1815 | 0.8990 | 0.5700 | 0.1720 | 0.0015 |
| benchmark | bpic2017_refused | Best tuned GBM + isotonic | 0.8532 ± 0.0012 | 0.0170 ± 0.0008 | 0.0739 | 0.9430 | 0.5100 | -0.0000 | 0.0000 |
| benchmark | bpic2017_refused | LGBM | 0.8550 ± 0.0015 | 0.0627 ± 0.0053 | 0.0956 | 0.8730 | 0.6430 | 0.0000 | 0.0000 |
| benchmark | bpic2017_refused | Stack (proposed) | 0.8531 ± 0.0021 | 0.0174 ± 0.0012 | 0.0739 | 0.8890 | 0.6200 | -0.0002 | 0.0000 |
| benchmark | bpic2017_refused | Stack of default GBMs (untuned) | 0.8518 | 0.0142 | 0.0737 | 0.8920 | 0.6220 | 0.0001 | 0.0000 |
| benchmark | bpic2017_refused | Stack w/o Transformer | 0.8537 ± 0.0017 | 0.0170 ± 0.0007 | 0.0739 | 0.8780 | 0.6390 | -0.0000 | 0.0000 |
| benchmark | bpic2017_refused | Stack w/o post-calibration | 0.8535 ± 0.0017 | 0.0168 ± 0.0010 | 0.0739 | 0.8790 | 0.6390 | -0.0001 | 0.0000 |
| benchmark | bpic2017_refused | Transformer | 0.7377 ± 0.0025 | 0.0135 ± 0.0028 | 0.1025 | 0.9070 | 0.4530 | -0.0003 | 0.0000 |
| benchmark | sepsis_cases_1 | Best tuned GBM + isotonic | 0.4807 ± 0.0119 | 0.1816 ± 0.0257 | 0.1467 | 0.8800 | 0.2430 | -0.0873 | -0.0185 |
| benchmark | sepsis_cases_1 | LGBM | 0.3632 ± 0.0469 | 0.0575 ± 0.0148 | 0.1010 | 0.7970 | 0.3900 | 0.0000 | 0.0000 |
| benchmark | sepsis_cases_1 | Stack (proposed) | 0.4173 ± 0.0234 | 0.1357 ± 0.0390 | 0.1259 | 0.7300 | 0.4000 | -0.0251 | -0.0121 |
| benchmark | sepsis_cases_1 | Stack of default GBMs (untuned) | 0.4547 | 0.1095 | 0.1253 | 0.8780 | 0.1760 | -0.0217 | -0.0127 |
| benchmark | sepsis_cases_1 | Stack w/o Transformer | 0.4238 ± 0.0316 | 0.1231 ± 0.0398 | 0.1197 | 0.7230 | 0.4030 | -0.0150 | -0.0070 |
| benchmark | sepsis_cases_1 | Stack w/o post-calibration | 0.4147 ± 0.0223 | 0.1705 ± 0.0319 | 0.1421 | 0.7280 | 0.4220 | -0.0459 | -0.0229 |
| benchmark | sepsis_cases_1 | Transformer | 0.3960 ± 0.0218 | 0.0905 ± 0.0121 | 0.1123 | 0.6900 | 0.4200 | -0.0150 | 0.0000 |
| benchmark | sepsis_cases_2 | Best tuned GBM + isotonic | 0.8067 ± 0.0227 | 0.0953 ± 0.0364 | 0.0904 | 0.8510 | 0.7440 | 0.0282 | 0.0038 |
| benchmark | sepsis_cases_2 | LGBM | 0.8296 ± 0.0141 | 0.0633 ± 0.0160 | 0.0679 | 0.8440 | 0.9380 | 0.0342 | 0.0167 |
| benchmark | sepsis_cases_2 | Stack (proposed) | 0.8301 ± 0.0310 | 0.0843 ± 0.0368 | 0.0873 | 0.8020 | 0.9180 | 0.0288 | 0.0058 |
| benchmark | sepsis_cases_2 | Stack of default GBMs (untuned) | 0.8531 | 0.0338 | 0.0554 | 0.8480 | 0.9340 | 0.0474 | 0.0321 |
| benchmark | sepsis_cases_2 | Stack w/o Transformer | 0.8326 ± 0.0272 | 0.0828 ± 0.0267 | 0.0854 | 0.8130 | 0.9050 | 0.0304 | 0.0064 |
| benchmark | sepsis_cases_2 | Stack w/o post-calibration | 0.8301 ± 0.0310 | 0.0843 ± 0.0368 | 0.0873 | 0.8020 | 0.9180 | 0.0288 | 0.0058 |
| benchmark | sepsis_cases_2 | Transformer | 0.8372 ± 0.0047 | 0.0329 ± 0.0081 | 0.0697 | 0.9120 | 0.9120 | 0.0372 | 0.0128 |
| benchmark | sepsis_cases_3 | Best tuned GBM + isotonic | 0.6624 ± 0.0236 | 0.0854 ± 0.0137 | 0.1620 | 0.9250 | 0.2170 | -0.0004 | -0.0102 |
| benchmark | sepsis_cases_3 | LGBM | 0.6401 ± 0.0266 | 0.0506 ± 0.0053 | 0.1436 | 0.8530 | 0.3930 | 0.0048 | -0.0013 |
| benchmark | sepsis_cases_3 | Stack (proposed) | 0.7162 ± 0.0060 | 0.0627 ± 0.0083 | 0.1383 | 0.8570 | 0.4350 | 0.0138 | -0.0025 |
| benchmark | sepsis_cases_3 | Stack of default GBMs (untuned) | 0.7065 | 0.0416 | 0.1387 | 0.9250 | 0.2640 | 0.0102 | -0.0064 |
| benchmark | sepsis_cases_3 | Stack w/o Transformer | 0.6824 ± 0.0218 | 0.0651 ± 0.0152 | 0.1457 | 0.8880 | 0.3320 | 0.0071 | -0.0013 |
| benchmark | sepsis_cases_3 | Stack w/o post-calibration | 0.7162 ± 0.0060 | 0.0627 ± 0.0083 | 0.1383 | 0.8570 | 0.4350 | 0.0138 | -0.0025 |
| benchmark | sepsis_cases_3 | Transformer | 0.6977 ± 0.0333 | 0.0738 ± 0.0203 | 0.1440 | 0.8500 | 0.3510 | 0.0020 | 0.0000 |
| benchmark | traffic_fines_1 | Best tuned GBM + isotonic | 0.7905 ± 0.0057 | 0.0751 ± 0.0105 | 0.1877 | 0.8880 | 0.6080 | 0.2268 | 0.1126 |
| benchmark | traffic_fines_1 | LGBM | 0.7843 ± 0.0041 | 0.0797 ± 0.0178 | 0.1898 | 0.8860 | 0.5960 | 0.2010 | 0.1121 |
| benchmark | traffic_fines_1 | Stack (proposed) | 0.7932 ± 0.0025 | 0.0679 ± 0.0048 | 0.1842 | 0.8920 | 0.5920 | 0.2268 | 0.1126 |
| benchmark | traffic_fines_1 | Stack of default GBMs (untuned) | 0.7827 | 0.0722 | 0.1897 | 0.9820 | 0.2570 | 0.2268 | 0.1126 |
| benchmark | traffic_fines_1 | Stack w/o Transformer | 0.7878 ± 0.0021 | 0.0704 ± 0.0084 | 0.1867 | 0.8960 | 0.5790 | 0.2268 | 0.1126 |
| benchmark | traffic_fines_1 | Stack w/o post-calibration | 0.7938 ± 0.0028 | 0.0714 ± 0.0044 | 0.1826 | 0.8750 | 0.6500 | 0.2268 | 0.1126 |
| benchmark | traffic_fines_1 | Transformer | 0.7928 ± 0.0018 | 0.0661 ± 0.0159 | 0.1825 | 0.8760 | 0.6250 | 0.2267 | 0.1125 |
| strict | bpic2012_accepted | Best tuned GBM + isotonic | 0.5649 ± 0.0127 | 0.0656 ± 0.0184 | 0.2509 | 0.9250 | 0.2000 | 0.1854 | -0.0029 |
| strict | bpic2012_accepted | LGBM | 0.5694 ± 0.0055 | 0.0499 ± 0.0052 | 0.2468 | 0.8830 | 0.2970 | 0.1858 | 0.0046 |
| strict | bpic2012_accepted | Stack (proposed) | 0.5710 ± 0.0117 | 0.0483 ± 0.0107 | 0.2472 | 0.8880 | 0.2890 | 0.1860 | 0.0049 |
| strict | bpic2012_accepted | Stack of default GBMs (untuned) | 0.5749 | 0.0422 | 0.2454 | 0.8820 | 0.3050 | 0.1859 | 0.0059 |
| strict | bpic2012_accepted | Stack w/o Transformer | 0.5699 ± 0.0129 | 0.0497 ± 0.0119 | 0.2474 | 0.8880 | 0.2880 | 0.1862 | 0.0068 |
| strict | bpic2012_accepted | Stack w/o post-calibration | 0.5710 ± 0.0117 | 0.0483 ± 0.0107 | 0.2472 | 0.8880 | 0.2890 | 0.1860 | 0.0049 |
| strict | bpic2012_accepted | Transformer | 0.5649 ± 0.0038 | 0.0892 ± 0.0359 | 0.2540 | 0.8860 | 0.2920 | 0.1856 | -0.0050 |
| strict | bpic2017_accepted | Best tuned GBM + isotonic | 0.6790 ± 0.0011 | 0.0209 ± 0.0018 | 0.2169 | 0.9200 | 0.3320 | 0.2988 | 0.1104 |
| strict | bpic2017_accepted | LGBM | 0.6805 ± 0.0012 | 0.0263 ± 0.0063 | 0.2170 | 0.8860 | 0.4240 | 0.2986 | 0.1115 |
| strict | bpic2017_accepted | Stack (proposed) | 0.6810 ± 0.0007 | 0.0155 ± 0.0011 | 0.2159 | 0.8840 | 0.4300 | 0.2988 | 0.1112 |
| strict | bpic2017_accepted | Stack of default GBMs (untuned) | 0.6805 | 0.0152 | 0.2161 | 0.8850 | 0.4240 | 0.2987 | 0.1119 |
| strict | bpic2017_accepted | Stack w/o Transformer | 0.6810 ± 0.0008 | 0.0158 ± 0.0008 | 0.2159 | 0.8850 | 0.4290 | 0.2988 | 0.1113 |
| strict | bpic2017_accepted | Stack w/o post-calibration | 0.6810 ± 0.0007 | 0.0155 ± 0.0011 | 0.2159 | 0.8840 | 0.4300 | 0.2988 | 0.1112 |
| strict | bpic2017_accepted | Transformer | 0.6621 ± 0.0018 | 0.0351 ± 0.0037 | 0.2215 | 0.8980 | 0.3720 | 0.2957 | 0.1036 |
| strict | sepsis_cases_1 | Best tuned GBM + isotonic | 0.4790 ± 0.0588 | 0.1495 ± 0.0153 | 0.1276 | 0.9290 | 0.2010 | -0.0345 | -0.0038 |
| strict | sepsis_cases_1 | LGBM | 0.3905 ± 0.0435 | 0.0826 ± 0.0139 | 0.1041 | 0.8320 | 0.2950 | -0.0039 | -0.0006 |
| strict | sepsis_cases_1 | Stack (proposed) | 0.4919 ± 0.0332 | 0.1092 ± 0.0198 | 0.1169 | 0.8670 | 0.2950 | -0.0176 | -0.0102 |
| strict | sepsis_cases_1 | Stack of default GBMs (untuned) | 0.4309 | 0.0908 | 0.1053 | 0.7940 | 0.4070 | 0.0000 | 0.0000 |
| strict | sepsis_cases_1 | Stack w/o Transformer | 0.4934 ± 0.0437 | 0.1083 ± 0.0189 | 0.1187 | 0.8540 | 0.3510 | -0.0250 | -0.0115 |
| strict | sepsis_cases_1 | Stack w/o post-calibration | 0.4819 ± 0.0447 | 0.1158 ± 0.0236 | 0.1215 | 0.8290 | 0.3400 | -0.0252 | -0.0115 |
| strict | sepsis_cases_1 | Transformer | 0.4122 ± 0.0127 | 0.0781 ± 0.0089 | 0.1073 | 0.7720 | 0.3720 | -0.0055 | 0.0000 |
| strict | traffic_fines_1 | Best tuned GBM + isotonic | 0.7829 ± 0.0074 | 0.0551 ± 0.0179 | 0.1889 | 0.8780 | 0.5640 | 0.1446 | 0.0170 |
| strict | traffic_fines_1 | LGBM | 0.7769 ± 0.0089 | 0.1155 ± 0.0270 | 0.2059 | 0.8790 | 0.5570 | 0.1230 | 0.0157 |
| strict | traffic_fines_1 | Stack (proposed) | 0.7914 ± 0.0012 | 0.0541 ± 0.0209 | 0.1860 | 0.8700 | 0.5910 | 0.1446 | 0.0173 |
| strict | traffic_fines_1 | Stack of default GBMs (untuned) | 0.7667 | 0.0970 | 0.2038 | 0.8620 | 0.5850 | 0.1448 | 0.0172 |
| strict | traffic_fines_1 | Stack w/o Transformer | 0.7804 ± 0.0063 | 0.0694 ± 0.0170 | 0.1910 | 0.8550 | 0.6120 | 0.1446 | 0.0171 |
| strict | traffic_fines_1 | Stack w/o post-calibration | 0.7914 ± 0.0013 | 0.0545 ± 0.0156 | 0.1850 | 0.8660 | 0.6020 | 0.1446 | 0.0174 |
| strict | traffic_fines_1 | Transformer | 0.7908 ± 0.0012 | 0.0776 ± 0.0375 | 0.1900 | 0.8790 | 0.5840 | 0.1446 | 0.0151 |


BENCHMARK averages over the 10 tasks:

| variant | auc_mean | ece_mean | brier_mean | singleton_rate_a0_1_mean | nb_r0_3_mean |
|---|---|---|---|---|---|
| Best tuned GBM + isotonic | 0.7345 | 0.0612 | 0.1448 | 0.4730 | 0.0819 |
| LGBM | 0.7229 | 0.0609 | 0.1403 | 0.5801 | 0.0886 |
| Stack (proposed) | 0.7393 | 0.0528 | 0.1391 | 0.5836 | 0.0892 |
| Stack of default GBMs (untuned) | 0.7424 | 0.0427 | 0.1363 | 0.5209 | 0.0906 |
| Stack w/o Transformer | 0.7351 | 0.0514 | 0.1394 | 0.5708 | 0.0900 |
| Stack w/o post-calibration | 0.7391 | 0.0566 | 0.1406 | 0.5935 | 0.0871 |
| Transformer | 0.7105 | 0.0464 | 0.1458 | 0.5429 | 0.0900 |


## 13. Environment and runtime

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


## 14. Files

`results/ALL_*.csv`: tidy tables behind every table and figure (per-seed metrics, summaries, bootstrap CIs, pairwise tests, Friedman/Nemenyi/Wilcoxon, calibration, reliability, conformal, deferral, risk–coverage, cost, ablation, XAI, best params, Optuna trials, dataset stats). `results/per_task/<protocol>/<task>/`: the same per task, plus SHAP samples (`shap_sample.npz`) and the deferred-case waterfall data. `results/figures/`: PNG (300 dpi) + PDF. Code: `src/` (parse_logs.py, prepare.py, train_gbm.py, train_deep.py, evaluate.py, explain.py, aggregate.py, figures.py, make_tables.py, build_summary.py).

All figures are in `results/figures/` as 300 dpi PNG and PDF:
- `fig01_cd_diagram_benchmark`, `fig01_cd_diagram_strict`: Nemenyi critical-difference diagrams of average AUC rank (8 models; 10 BENCHMARK and 4 STRICT tasks).
- `fig02_auc_heatmap_benchmark`, `fig02_auc_heatmap_strict`: test AUC (mean of 5 seeds), models × tasks, with the best model per task in bold.
- `fig03_auc_vs_prefix_benchmark`, `fig03_auc_vs_prefix_strict`: AUC by prefix length, proposed stack vs the 3 best baselines per task, with 95% case-bootstrap bands (seed 0).
- `fig04_reliability`: reliability diagrams for raw LGBM, the stack's meta-learner output and the calibrated stack on 4 representative BENCHMARK tasks.
- `fig05a_shap_beeswarm`: ensemble TreeSHAP beeswarm plots for 4 representative BENCHMARK tasks. Includes the leaky benchmark features; see Section 5.3 of the paper.
- `fig05b_shap_dependence`: dependence plot of the top feature for STRICT bpic2017_accepted.
- `fig05c_waterfall_deferred_case`: local waterfall of a case deferred by the conformal rule (STRICT bpic2017_accepted).
- `fig06_explanation_quality`: SHAP vs LIME stability boxplots (under perturbation and across training/sampling seeds) and deletion-fidelity curves.
- `fig07_risk_coverage_conformal`: risk–coverage curves with 95% bands for 4 tasks, plus empirical vs nominal Mondrian conformal coverage for all 10 BENCHMARK tasks.
- `fig08_net_benefit`: decision curves (net benefit vs cost ratio) for the proposed q > r rule, baselines, always/never intervene and the oracle.
- `fig09_ablation`: ablation bar charts (AUC, ECE, conformal automation rate) with per-task dots.
