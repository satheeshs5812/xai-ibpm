## Table 10. Effect of the evaluation protocol on the stack and top ensemble-SHAP features

| Task | AUC BENCHMARK | AUC STRICT | Δ AUC | Top features BENCHMARK | Top features STRICT |
|---|---|---|---|---|---|
| BPIC12-acc | 0.705 | 0.571 | -0.134 | #O_SENT_BACK-COMPLETE (0.46); AMOUNT_REQ (0.14); #W_Valideren aanvraag-SCHEDULE (0.10); #O_ACCEPTED-COMPLETE (0.08) | AMOUNT_REQ (0.14); month_max (0.06); #O_SENT_BACK-COMPLETE (0.06); timesincemidnight_max (0.06) |
| BPIC17-acc | 0.899 | 0.681 | -0.218 | #Selected=False (0.89); CreditScore_mean (0.85); CreditScore_sum (0.41); #O_Create Offer (0.27) | #O_Create Offer (0.28); #res User_1 (0.16); ApplicationType=New credit (0.11); RequestedAmount (0.08) |
| Sepsis-1 | 0.417 | 0.492 | +0.075 | weekday_mean (0.12); SIRSCritHeartRate=False (0.12); open_cases_min (0.10); DiagnosticECG=False (0.10) | weekday_mean (0.09); Age (0.09); SIRSCritHeartRate=False (0.09); month_mean (0.09) |
| Traffic | 0.793 | 0.791 | -0.002 | #Payment (0.56); #Send Fine (0.35); idx_act_lag1 (0.29); #lastSent=N (0.19) | idx_act_lag1 (0.19); #Payment (0.19); idx_act_lag3 (0.07); amount (0.06) |
