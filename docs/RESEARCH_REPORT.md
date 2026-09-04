# Physics-Informed Machine Learning for HVAC Energy Optimization: Forecasting, Supply-Air-Temperature Reset, and Chiller Sequencing

**Author:** Sabbir Hossain
**Date:** September 2026
**Code & data (local):** `D:\Python research project` — `src/hvac_optimizer/`, `examples/run_demo.py`, `notebooks/01_hvac_energy_study.ipynb`
**Climate:** Hot-humid, Dhaka-like (synthetic BMS data, 2000 m² commercial building)

---

## Abstract

Heating, ventilation, and air-conditioning (HVAC) accounts for 40–60% of commercial building electricity in hot-humid climates. This study presents a physics-informed machine-learning pipeline that (i) models zone thermodynamics with a 2R2C lumped network and ASHRAE psychrometrics, (ii) forecasts hourly cooling load with gradient boosting, and (iii) applies supervisory control — supply-air-temperature (SAT) reset, minimum-chiller sequencing, and look-ahead pre-cooling. On a 60-day hourly test the forecaster achieves MAE 1.55 kW, RMSE 2.76 kW, R² 0.9907, CVRMSE 8.30% and NMBE 2.29%, passing ASHRAE Guideline 14 hourly calibration limits (30% / 10%). SAT-reset control reduces HVAC electricity by 11.11% on the test slice (13.97% full-year); optimal chiller sequencing saves 24.49% relative to an all-chillers-committed baseline. Weekly load history (lag-168 h, 45.8% importance) dominates occupancy and outdoor temperature, confirming that schedule-aware control is the highest-leverage retrofit. All experiments are reproducible on a laptop with 5/5 pytest tests passing.

**Keywords:** HVAC, energy optimization, cooling-load forecasting, gradient boosting, supply-air-temperature reset, chiller sequencing, ASHRAE Guideline 14, model predictive control.

---

## 1. Introduction

Commercial buildings consume roughly one-third of global final energy, and HVAC is the single largest end use. In Bangladesh, where cooling degree-days are rising and grid peaks are driven by air-conditioning, even 10% HVAC savings translate into avoided generation, lower bills, and reduced CO₂. Two barriers persist: (a) operators lack calibrated load forecasts at supervisory timescales, and (b) fixed-setpoint control (constant SAT, all chillers on) wastes part-load and mild-hour efficiency.

This work asks three research questions:

- **RQ1.** Can a lightweight forecaster (no deep learning, no cloud) reach ASHRAE G14 calibration quality on hourly data?
- **RQ2.** How much energy do classical supervisory strategies (SAT reset, sequencing) save over a realistic baseline?
- **RQ3.** Which features drive cooling load, and what does that imply for deployment?

Contribution: an open, laptop-reproducible package (`hvac-energy-optimizer`) unifying psychrometrics, a 2R2C simulator, a forecaster, and three controllers with a unified evaluation harness.

## 2. Related work

Supervisory control for HVAC has a long lineage (Braun et al.; ASHRAE Guideline 36). SAT reset trades chiller lift against fan power and reheat; chiller sequencing exploits the concave part-load COP curve. Load forecasting spans ARX, SVR, gradient boosting, and LSTM; for hourly horizons with calendar structure, boosted trees remain Pareto-optimal on accuracy vs. complexity (no GPU, interpretable importances). Calibration is judged by ASHRAE Guideline 14 CVRMSE/NMBE. Model predictive control adds pre-cooling but needs a model — here a 2R2C network standard in MPC literature. This study deliberately avoids heavy solvers (CasADi/pyomo) to stay laptop-runnable, using a greedy look-ahead proxy that preserves the load-shifting insight.

## 3. Methodology

### 3.1 Psychrometrics (ASHRAE Fundamentals Ch. 1)

Tetens saturation pressure `psat = 610.78·exp(17.27·T/(T+237.3))` Pa (error <1% in 0–45 °C vs. Hyland–Wexler), humidity ratio `W = 0.621945·pv/(p−pv)`, enthalpy `h = 1.006·T + W·(2501+1.86·T)` kJ/kg-da, Magnus dew-point, and coil load `Q = m_dot·(h_in−h_out)`. Implemented in `psychrometrics.py` with vectorised NumPy and unit tests.

### 3.2 Building and plant model

2R2C zone (`thermal_model.py`):

```
C_in·dT_in/dt   = (T_wall−T_in)/R_in + Q_int + Q_sol + Q_hvac
C_wall·dT_wall/dt = (T_out−T_wall)/R_out + (T_in−T_wall)/R_in
```

Defaults R_in 1.5, R_out 2.5 K/kW, C_in 2, C_wall 8 kWh/K. Chiller COP:

```
COP = COP_rated · (0.45+0.85·PLR−0.30·PLR²) · (1−k·(T_out−35))
```

with k = 0.012 (baseline) / 0.010 (SAT-reset, better lift), capturing part-load and condenser effects. Deadband proportional control (8 kW/K, 200 kW cap) closes the loop in `simulate_zone()`.

### 3.3 Synthetic BMS dataset

`synthetic.py` generates hourly `t_out, rh_out, occupancy_frac, q_internal, q_solar, cooling_load_kw` for a 2000 m² office: Dhaka-like mean 27 °C ± seasonal/diurnal/noise, weekday 08–18 occupancy with holidays, solar bell at 13:00, UA envelope + ventilation-latent terms. Reproducible via seed. Year used: 8760 h, mean load 42.2 kW.

### 3.4 Forecaster

`forecasting.py`: cyclical hour/dow/month (sin/cos), weekend/occupied flags, lags 1/24/168 h. `CoolingLoadForecaster` wraps GBM (default), RF, Ridge with `TimeSeriesSplit` CV, `evaluate()` (MAE/RMSE/CVRMSE/NMBE/R²) and importances. Chronological 80/20 split avoids leakage.

### 3.5 Controllers

- **Baseline:** fixed SAT 13 °C, all 2×175 kW chillers committed, constant-volume fan (2% peak).
- **SAT reset:** SAT 12→16 °C by OAT, VAV fan ∝ flow³ (2.5% peak coeff), 2% COP uplift.
- **Sequencing:** commit fewest chillers above 15% PLR, split evenly, pick max-COP commit.
- **SimpleMPC (`mpc.py`):** pre-cool at 60% capacity when OAT ≥ 32 °C enters 4-h horizon, comfort 22–25.5 °C.

### 3.6 Metrics

ASHRAE G14 hourly: CVRMSE = RMSE/mean·100 ≤ 30%, |NMBE| ≤ 10% with NMBE = Σ(y−ŷ)/((n−1)·mean)·100. Energy saving = (E_base−E_opt)/E_base·100.

## 4. Experimental setup

Machine: Windows laptop, Python 3.11.9, scikit-learn 1.9, pandas 3.0. Main file `examples/run_demo.py --days 60 --model gbm`; full-year via `scripts/train_forecaster.py` and `scripts/evaluate_controls.py`; tests `pytest -q`. No GPU, runtime < 1 min.

## 5. Results

### 5.1 Forecasting (RQ1)

| Split | MAE (kW) | RMSE (kW) | CVRMSE (%) | NMBE (%) | R² | G14 |
|---|---|---|---|---|---|---|
| 60-day test | 1.55 | 2.76 | 8.30 | +2.29 | 0.9907 | PASS |
| Full-year test | 1.71 | 2.95 | 9.82 | −1.57 | 0.9877 | PASS |

Both pass with wide margin. Figure 1 (top) shows 1-week actual vs. predicted overlap.

Feature importances (GBM): lag168 45.8%, q_internal 18.4%, is_occupied 17.9%, t_out 8.1%, occupancy_frac 7.0%, q_solar 1.9%, lag1 0.7%, lag24 0.2%, rh_out ~0%. Weekly periodicity dominates.

### 5.2 Control savings (RQ2)

| Strategy | 60-day kWh | Saving | Full-year kWh | Saving |
|---|---|---|---|---|
| Baseline | 4291.1 | — | 191582.8 | — |
| SAT reset | 3814.5 | **11.11%** | 164825.4 | **13.97%** |
| Sequencing | — | — | 144655.4 | **24.49%** |

Figure 1 (bottom) shows peak shaving. Sequencing gain is large because the baseline commits both chillers at low PLR (≈12% mean PLR on a 350 kW plant); the optimiser typically runs one chiller near 25% PLR. SAT-reset gain (≈11–14%) matches literature for hot-humid VAV retrofits.

### 5.3 Simulation sanity

`simulate_zone()` on 48 h at 34 °C with 30 kW gains engages cooling after the first hour and holds COP 1.5–5. All 5 pytest tests pass (psychrometrics, energy balance, forecaster R²>0.5, finiteness, G14).

## 6. Discussion (RQ3 + limitations)

**What it means.** Schedule (who is in the building, what week it is) beats weather for load prediction — log occupancy and keep ≥3 weeks history before deploying MPC. An 11–14% SAT-reset saving needs only a setpoint schedule change: cheapest decarbonisation available. Sequencing needs no new iron, only commitment logic.

**Limitations.** Synthetic climate and idealised fan/COP proxies overstate absolute kWh; relative savings are the claim. No humidity control, no demand charge, no thermal-comfort (PMV) constraint beyond temperature band, no real-BMS validation yet. GBM lags (especially lag168) require backfill on deployment.

**Threats to validity.** Single climate/seed; part-load curve from literature not calibrated; fan coefficients are proxies. Mitigation: full equations and seeds published; replace `data/synthetic_hvac.csv` with measured trends to re-run unchanged.

## 7. Conclusion and future work

A laptop-scale, physics-informed pipeline passes ASHRAE G14 and demonstrates 11–14% HVAC savings from SAT reset (24% from sequencing vs. naive staging). Next: (i) validate on measured BMS data, (ii) add PMV/CO₂ comfort constraints and demand-response pricing, (iii) full MPC in CasADi, (iv) fault-detection (stuck damper, fouling) as a second study.

## References

1. ASHRAE Handbook — Fundamentals (2021), Ch. 1 Psychrometrics.
2. ASHRAE Guideline 14-2014, Measurement of Energy, Demand, and Water Savings.
3. ASHRAE Guideline 36-2024, High-Performance Sequences of Operation.
4. J. E. Braun et al., Methods for supervisory control of building systems.
5. F. Pedregosa et al., Scikit-learn: Machine learning in Python, JMLR 12 (2011).
6. Y. Ma et al., Model predictive control for building energy systems (survey).

## Appendix A — Reproduce (this laptop)

```
C:\Users\hp\AppData\Local\Programs\Python\Python311\python.exe scripts/generate_synthetic_data.py --days 365
C:\Users\hp\AppData\Local\Programs\Python\Python311\python.exe scripts/train_forecaster.py --csv data/synthetic_hvac.csv --model gbm
C:\Users\hp\AppData\Local\Programs\Python\Python311\python.exe scripts/evaluate_controls.py --csv data/synthetic_hvac.csv
C:\Users\hp\AppData\Local\Programs\Python\Python311\python.exe examples/run_demo.py --days 60 --model gbm
C:\Users\hp\AppData\Local\Programs\Python\Python311\python.exe -m pytest -q
```

## Appendix B — Package layout

`src/hvac_optimizer/{psychrometrics,thermal_model,forecasting,optimization,mpc,evaluation,synthetic}.py`, `scripts/{generate_synthetic_data,train_forecaster,evaluate_controls,make_report}.py`, `examples/run_demo.py`, `tests/test_hvac.py`, `notebooks/01_hvac_energy_study.ipynb`, `docs/METHODOLOGY.md`, `results/{metrics.json,demo.png}`.
