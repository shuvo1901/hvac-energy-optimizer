# Physics-Informed Machine Learning for HVAC Energy Optimization: Load Forecasting with Supervisory Reset and Sequencing Control

**Md. Sabbir Hossain**
*Independent Researcher — Dhaka, Bangladesh | Shuvo.Hossain101@gmail.com*

**Abstract—** HVAC systems account for 40-60% of commercial building electricity in hot-humid climates, yet most operate on fixed setpoints that waste part-load and mild-hour efficiency. We present a laptop-reproducible, physics-informed pipeline that unifies (i) ASHRAE psychrometrics and a 2R2C zone model, (ii) a gradient-boosting hourly cooling-load forecaster, and (iii) supervisory control via supply-air-temperature (SAT) reset, minimum-chiller sequencing, and look-ahead pre-cooling. Evaluated on synthetic BMS data for a 2000 m2 office in a Dhaka-like climate (8760 h, mean load 42.2 kW), the forecaster achieves MAE 1.55 kW, RMSE 2.76 kW, R2 0.9907, CVRMSE 8.30% and NMBE 2.29% on a 60-day test, satisfying ASHRAE Guideline 14 hourly limits (30%/10%). SAT reset reduces HVAC electricity by 11.11% on the test slice (13.97% full-year); optimal sequencing saves 24.49% versus an all-chillers-committed baseline. Feature analysis shows weekly history (168-h lag, 45.8%) dominates occupancy and outdoor temperature, motivating schedule-aware control. The package (7 modules, 5/5 pytest passing) runs in under one minute without GPU.

**Keywords—** HVAC energy optimization; cooling load forecasting; gradient boosting; supply air temperature reset; chiller sequencing; ASHRAE Guideline 14; model predictive control; building energy management.

## I. INTRODUCTION

Commercial buildings consume roughly one third of global final energy, with HVAC as the largest end use. In Bangladesh, rising cooling degree-days make air-conditioning the main driver of grid peaks and commercial tariffs. A 10% HVAC saving therefore defers generation investment and cuts emissions at scale.

Two gaps block deployment. First, operators lack calibrated short-horizon load forecasts that supervisory controllers can trust. Second, prevalent practice — constant SAT (~13 C) with all chillers committed — ignores the concave part-load COP curve and mild-hour lift reduction.

We address three questions: (Q1) Can a lightweight forecaster without deep learning reach Guideline-14 quality? (Q2) What do classical supervisory retrofits save against a fair baseline? (Q3) Which signals drive load and what follows for deployment?

Contributions: (1) an open 7-module Python package unifying psychrometrics, 2R2C simulation, forecasting, and three controllers with one evaluation harness; (2) controlled comparison of SAT reset and sequencing with part-load-consistent baselines; (3) full laptop reproducibility (seeded data, 5 tests, <1 min runtime).

## II. RELATED WORK

Supervisory HVAC control dates to Braun's optimal setpoint work and is codified in ASHRAE Guideline 36. SAT reset trades chiller lift and reheat against fan energy; sequencing exploits COP(PLR). Forecasting spans ARX, SVR, GBM, and LSTM; at hourly horizons with strong calendar structure, boosted trees remain Pareto-optimal for accuracy, interpretability, and cost. Calibration follows Guideline 14 (CVRMSE/NMBE). MPC typically uses RC networks; we adopt 2R2C and a solver-free greedy look-ahead that preserves the pre-cooling insight while staying dependency-light (no CasADi/pyomo).

## III. METHODOLOGY

### A. Psychrometrics

Per ASHRAE Fundamentals Ch.1: Tetens psat = 610.78 exp(17.27 T/(T+237.3)) Pa (<1% error, 0-45 C), W = 0.621945 pv/(p-pv), h = 1.006 T + W(2501+1.86 T) kJ/kg-da, Magnus dew-point, coil Q = m_dot (h_in - h_out).

### B. Zone and Plant Model

2R2C network: C_in dT_in/dt = (T_wall-T_in)/R_in + Q_int + Q_sol + Q_hvac; C_wall dT_wall/dt = (T_out-T_wall)/R_out + (T_in-T_wall)/R_in, with R_in 1.5, R_out 2.5 K/kW, C_in 2, C_wall 8 kWh/K. Chiller: COP = COP_rated (0.45+0.85 PLR-0.30 PLR^2)(1-k(T_out-35)), k = 0.012 baseline / 0.010 reset. Proportional control (8 kW/K, 200 kW cap). A state-propagation bug found during testing (frozen zone state) was fixed and regression-covered.

### C. Dataset

Synthetic hourly BMS trends (synthetic.py) for a 2000 m2 office: T_out seasonal+diurnal+noise (mean 27 C), RH anti-correlated, weekday 08-18 occupancy with holidays, solar bell peaking 13:00, UA envelope plus latent ventilation. Year: 8760 samples, mean 42.2 kW. Seeded (42) for exact replay; trivially replaceable by measured CSV with identical column names.

### D. Load Forecaster

Cyclical hour/day/month (sin/cos), weekend/occupied flags, lags 1/24/168 h. GradientBoostingRegressor default (RF/Ridge ablated), chronological 80/20 split, TimeSeriesSplit CV. Metrics: MAE, RMSE, CVRMSE, NMBE, R2.

### E. Controllers

Baseline: fixed SAT 13 C, both 175-kW chillers committed, constant-volume fan (2% peak). SAT reset: 12-16 C by OAT, VAV fan cube law (2.5% coeff), +2% COP lift. Sequencing: fewest chillers above 15% PLR. SimpleMPC: 60% pre-cool when 32 C enters 4-h horizon, comfort 22-25.5 C. Baselines share the part-load curve so only staging/reset differences are measured — a fairness fix that reversed an initial negative-saving artifact.

## IV. EXPERIMENTAL SETUP

Windows laptop, Python 3.11, scikit-learn 1.9, pandas 3.0. Main: examples/run_demo.py (60 days, GBM). Full-year: train_forecaster.py, evaluate_controls.py. Suite: 5 pytest cases. Runtime <60 s, no GPU. Artifacts: metrics.json, demo.png.

## V. RESULTS

### A. Forecasting (Q1)

60-day: MAE 1.55, RMSE 2.76 kW, CVRMSE 8.30%, NMBE +2.29%, R2 0.9907 — PASS. Full-year: 1.71, 2.95 kW, 9.82%, -1.57%, 0.9877 — PASS. Importances: lag-168 45.8%, q_internal 18.4%, is_occupied 17.9%, T_out 8.1%, occ_frac 7.0%. Weekly repetition dominates; weather is secondary.

TABLE I. Forecast accuracy (PASS = within G14 hourly limits).
Split | MAE | RMSE | CVRMSE | NMBE / R2 | G14
60-day | 1.55 kW | 2.76 kW | 8.30% | +2.29% / 0.9907 | PASS
Full-year | 1.71 kW | 2.95 kW | 9.82% | -1.57% / 0.9877 | PASS

Fig. 1 (top): 1-week actual vs predicted traces overlap; (bottom): baseline vs reset power with visible peak shaving.

### B. Control Savings (Q2)

TABLE II. Energy (kWh) and savings.
Strategy | 60-day | Save | Full-year | Save
Baseline | 4291.1 | - | 191582.8 | -
SAT reset | 3814.5 | 11.11% | 164825.4 | 13.97%
Sequencing | - | - | 144655.4 | 24.49%

SAT-reset 11-14% aligns with hot-humid VAV literature. Sequencing is larger because the baseline stages both chillers at ~12% mean PLR; the optimizer typically runs one near 25%.

### C. Ablation and Sanity

Ridge baseline passes G14 but trails GBM R2 by ~2-3 points; RF matches GBM within noise at 5x training cost. simulate_zone at 34 C engages cooling after hour one with COP in [1.5, 5]. All tests green.

## VI. DISCUSSION (Q3, Limitations)

Schedule and history outweigh instantaneous weather: keep >=3 weeks of BMS trends and log occupancy before MPC. SAT reset is the cheapest tonne of CO2 — a schedule change only. Limitations: synthetic climate, proxy fan/COP coefficients (absolute kWh indicative; relative savings are the claim), no humidity/demand/PMV constraints, single seed. Mitigation: equations, seeds, and swap-in CSV path published.

## VII. CONCLUSION

A dependency-light, physics-informed pipeline clears ASHRAE G14 and demonstrates 11-14% savings from SAT reset (24% sequencing vs naive staging) on laptop hardware. Future: real-BMS validation, PMV/CO2 and tariff-aware MPC in CasADi, and automated fault detection.

## ACKNOWLEDGMENT

The author thanks the open-source scientific Python community (NumPy, pandas, scikit-learn, matplotlib).

## REFERENCES

[1] ASHRAE Handbook—Fundamentals, Ch. 1, 2021.
[2] ASHRAE Guideline 14-2014, Measurement of Energy, Demand, and Water Savings.
[3] ASHRAE Guideline 36-2024, High-Performance Sequences of Operation.
[4] J. E. Braun et al., "Methods for supervisory control of building HVAC systems," ASHRAE Trans.
[5] F. Pedregosa et al., "Scikit-learn: Machine learning in Python," JMLR, vol. 12, 2011.
[6] Y. Ma et al., "Model predictive control for building energy systems: A survey," Appl. Energy.
