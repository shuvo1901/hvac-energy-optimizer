# Methodology

Author: **Sabbir Hossain**

This project studies HVAC energy optimization for a 2000 m² commercial
building using a physics-informed ML pipeline.

## 1. Nomenclature

| Symbol | Meaning | Unit |
|---|---|---|
| $T_{out}, T_{in}$ | Outdoor / zone temperature | °C |
| $W$ | Humidity ratio | kg-w/kg-da |
| $h$ | Moist-air enthalpy | J/kg-da |
| $Q_c$ | Cooling load | kW |
| $P$ | Electric power | kW |
| CVRMSE / NMBE | ASHRAE Guideline 14 calibration metrics | % |

## 2. Psychrometrics (`psychrometrics.py`)

ASHRAE Fundamentals Ch.1 with Tetens saturation pressure
(error < 1% in 0–45 °C vs Hyland-Wexler) and Magnus dew-point.
Enthalpy: $h = 1.006T + W(2501+1.86T)$ kJ/kg.

## 3. Building model (`thermal_model.py`)

2R2C lumped model (standard for MPC studies):

```
C_in dT_in/dt  = (T_wall-T_in)/R_in + Q_int + Q_solar + Q_hvac
C_wall dT_wall/dt = (T_out-T_wall)/R_out + (T_in-T_wall)/R_in
```

Chiller COP model:

```
COP = COP_rated * (0.45+0.85·PLR−0.30·PLR²) * (1−0.012·(T_out−35))
```

capturing part-load and condenser-temperature effects.

## 4. Forecasting (`forecasting.py`)

GradientBoostingRegressor on [T_out, RH_out, occupancy, cyclical
hour/dow/month, lags 1/24/168h]. Train/test split is chronological
(TimeSeriesSplit CV) to avoid leakage. Reported: MAE/RMSE/CVRMSE/NMBE/R².

## 5. Supervisory control (`optimization.py`, `mpc.py`)

- **Baseline:** fixed SAT 13 °C, fixed COP curve.
- **SAT reset:** SAT 12→16 °C by OAT with cubic fan-power trade-off.
- **Chiller sequencing:** commit fewest chillers above 15% PLR.
- **SimpleMPC:** pre-cool ahead of OAT ≥ 32 °C within 22–25.5 °C comfort band.

## 6. Validation

- Unit tests (`tests/`) for psychrometrics, energy balance, COP bounds.
- ASHRAE G14 hourly limits: CVRMSE ≤ 30%, |NMBE| ≤ 10%.
- Synthetic data is documented as synthetic; replace `data/*.csv`
  with measured BMS trend data for publication (point list in §7).

## 7. Reproducing with real data

Required BMS trends (hourly, ≥ 3 months): `t_out, rh_out,
cooling_load_kw (or chilled-water ΔT×flow), occupancy, supply-air temp`.
Map columns to the same names and re-run `scripts/train_forecaster.py`.

## References

1. ASHRAE Handbook — Fundamentals (2021), Ch.1 Psychrometrics.
2. ASHRAE Guideline 14-2014, Measurement of Energy/Demand Savings.
3. Braun, J.E. et al., supervisory control for building systems.
4. Scikit-learn: Pedregosa et al., JMLR 2011.
