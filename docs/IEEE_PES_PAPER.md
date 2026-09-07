# Grid-Interactive HVAC Load Forecasting and Supervisory Control for Peak Reduction in Hot-Humid Commercial Buildings

**Md. Sabbir Hossain** — Independent Researcher, Dhaka, Bangladesh — Shuvo.Hossain101@gmail.com
*Target: IEEE PES General Meeting (5-page conference paper, PES Authors Kit) — Track: Applications of AI in the Power and Energy Industry / Energy Management*

**Abstract—** Commercial HVAC drives 40-60% of building electricity and a disproportionate share of distribution peaks in hot-humid grids. This paper presents a grid-interactive, physics-informed pipeline that couples ASHRAE psychrometrics and a 2R2C zone model with a gradient-boosting hourly cooling-load forecaster and supervisory control (supply-air-temperature reset, minimum-chiller sequencing, look-ahead pre-cooling). On a 2000 m2 office synthetic dataset (8760 h, Dhaka-like climate, 42.2 kW mean), forecasting reaches MAE 1.55 kW, RMSE 2.76 kW, R2 0.9907, CVRMSE 8.30%, NMBE 2.29% (60-day test), satisfying ASHRAE Guideline 14 (30%/10%). SAT reset cuts HVAC energy 11.11% (13.97% annual) and shaves weekly peaks; optimal sequencing saves 24.49% vs all-chillers-on. The 168-h load lag dominates importance (45.8%), enabling day-ahead bidding of flexible load. The 7-module open package runs in <1 min on a laptop (5/5 tests pass) and exposes hourly flexibility signals directly usable by distribution management and demand-response aggregators.

**Index Terms—** Building energy management, HVAC, load forecasting, gradient boosting, demand response, peak load reduction, chiller sequencing, ASHRAE Guideline 14.

## I. INTRODUCTION

Electrified cooling is now the fastest-growing end use on many South Asian feeders. In Dhaka, commercial HVAC sets the evening distribution peak, stresses transformers, and inflates demand charges. Grid-interactive efficient buildings (GEBs) that forecast load and reshape it are therefore a PES priority under "Powering the Digital Era" and the AI-in-grids super session.

Barriers: (i) operators lack trustworthy day-ahead building forecasts at meter/plant resolution; (ii) fixed SAT and naive staging waste part-load efficiency and offer no flexibility product to the grid. We ask: (Q1) can lightweight ML clear calibration-grade accuracy? (Q2) what energy AND peak (kW) reductions do supervisory retrofits deliver? (Q3) which signals make load predictable/dispatchable?

Contributions tailored to PES: (1) forecaster with ASHRAE-grade errors plus flexible-capacity outputs (kW shiftable by pre-cooling); (2) quantified energy + peak impacts against a part-load-consistent baseline; (3) open code mapping building kW to feeder-level DR potential.

## II. GRID CONTEXT AND RELATED WORK

PES literature treats buildings as distributed energy resources: GEBs, demand response, and virtual power plants. Guideline 36 sequences and Braun supervisory optima are the controls baseline; forecasting spans ARX to LSTM, with boosted trees Pareto-optimal hourly. Guideline 14 governs calibration claims. Unlike pure-ML papers, we retain a 2R2C model so MPC/pre-cooling has a thermal battery to dispatch — essential for credible flexibility (kWh shifted, kW shed, rebound characterized).

## III. METHODOLOGY

### A. Electrical-Thermal Interface

Building electric power is P = Q_cool/COP + P_fan. Psychrometrics (Tetens psat, W, h, Magnus dew-point, coil Q) give latent/sensible split; 2R2C gives Q_hvac dynamics: C_in dT_in/dt = (T_wall-T_in)/R_in + Q_int + Q_sol + Q_hvac. Chiller COP = rated x f(PLR) x f(OAT), f(PLR) = 0.45+0.85PLR-0.30PLR^2. Parameters: R 1.5/2.5 K/kW, C 2/8 kWh/K, 2x175 kW chillers, 8 kW/K control gain. Outputs per step: kW, COP, zone T — the feeder sees P(t) and a flexibility band.

### B. Data

Hourly synthetic BMS trends (2000 m2, Dhaka-like, seed 42): T_out, RH, occupancy, internal/solar gains, cooling load; 8760 h at 42.2 kW mean. Column-compatible with measured AMI/BMS exports for field replay.

### C. Day-Ahead Forecaster

Calendar-cyclical + lag 1/24/168-h features; GBM default; chronological 80/20 split; TimeSeriesSplit CV; MAE/RMSE/CVRMSE/NMBE/R2. Lag-168 captures weekly feeder periodicity critical for DR baselining.

### D. Supervisory / Flexibility Controllers

Baseline (business as usual): SAT 13 C, all chillers on, CV fan. SAT reset (EE retrofit): 12-16 C by OAT, VAV fan, +2% COP. Sequencing (staging fix): fewest chillers above 15% PLR. Pre-cooling MPC proxy: 60% pre-cool when 32 C enters 4-h horizon within 22-25.5 C — a load-shift offer (charge thermal mass off-peak, shed on-peak).

## IV. CASE STUDY SETUP

Laptop, Python 3.11, sklearn 1.9; examples/run_demo.py (60 d); train/evaluate scripts (full year); pytest (5 tests). Metrics: energy (kWh), peak (max kW over test week), G14 pair, savings %.

## V. RESULTS

### A. Forecast accuracy (Q1)

60-day: MAE 1.55, RMSE 2.76 kW, CVRMSE 8.30%, NMBE +2.29%, R2 0.9907 — PASS. Annual: 1.71, 2.95 kW, 9.82%, -1.57%, 0.9877 — PASS. Importances: lag168 45.8%, internal 18.4%, occupied 17.9%, T_out 8.1%. Week-ahead patterns enable CBL (customer baseline) accuracy for settlements.

TABLE I. Forecast vs ASHRAE G14 hourly (30%/10%).
Split | MAE | RMSE | CVRMSE | NMBE/R2 | G14
60-day | 1.55 | 2.76 | 8.30% | +2.29/0.9907 | PASS
Annual | 1.71 | 2.95 | 9.82% | -1.57/0.9877 | PASS

### B. Energy and peak impact (Q2)

TABLE II. Energy; weekly peak shaved ~10-12% under reset (Fig.1 bottom).
Strategy | 60-d kWh | Save | Annual kWh | Save
Baseline | 4291.1 | - | 191582.8 | -
SAT reset | 3814.5 | 11.11% | 164825.4 | 13.97%
Sequencing | - | - | 144655.4 | 24.49%

At 42 kW mean, 11-14% is ~4.6-5.9 kW average flexibility per building; 100-building aggregation gives ~0.5 MW DR — feeder-meaningful. Pre-cooling shifts ~20 kWh/day from afternoon peak to morning off-peak in simulation.

### C. What drives dispatchability (Q3)

Schedule/history >> weather: DR programs should target occupied-hour setpoint/fan dispatch and require >=3 weeks metering for baselines.

## VI. PRACTICAL IMPLICATIONS FOR PES

1) Utilities: use the forecaster as CBL + day-ahead feeder forecast input. 2) Aggregators: bid SAT-reset/pre-cool kW with rebound bounded by 2R2C. 3) Owners: sequencing + reset need no new iron. 4) Digital-era fit: hourly kW signals integrate with DMS/DERMS and data-center-adjacent commercial parks.

Limitations: synthetic data; proxy fan/COP (relative savings claimed); no network constraints, tariffs, or PMV. Field validation with AMI/BMS + OpenDSS feeder hosting is next.

## VII. CONCLUSION

Physics-informed ML clears calibration grade and unlocks 11-14% HVAC energy and ~10% peak reduction per building with laptop-grade tooling — a directly dispatchable GEB resource. Code, seeds, and swap-in CSV path are published for PES replication.

## REFERENCES

[1] ASHRAE Handbook—Fundamentals, Ch.1, 2021.
[2] ASHRAE Guideline 14-2014.
[3] ASHRAE Guideline 36-2024.
[4] J. E. Braun et al., Supervisory control of building HVAC, ASHRAE Trans.
[5] F. Pedregosa et al., Scikit-learn, JMLR 12, 2011.
[6] S. H. Hong et al., Grid-interactive efficient buildings, IEEE Electrific. Mag.
[7] Y. Ma et al., MPC for buildings survey, Appl. Energy.

## APPENDIX — PES SUBMISSION CHECKLIST (GM 2026, Montreal, "Powering the Digital Era")

- 5 pages MAX (incl. figs/refs), IEEE PES Authors Kit template ONLY (Word/LaTeX from ieee-pes.org, NOT generic IEEE template); US Letter, two-column, PDF Xplore-compatible via PDF eXpress.
- No Part 1/Part 2 papers; original work; AI-use disclosure per PES policy; IEEE copyright transfer after acceptance.
- Submit full paper to PES portal by deadline cycle (GM2026 was Nov 2025; watch pes-gm.org for next); acceptance ~March; poster presentation (Mon evening) MANDATORY or removed from Xplore; top 60-80 invited to best-paper oral (8 min).
- One author registration covers up to 2 papers; suggest track: AI in Power Grid Operation / Energy Management.
- This draft is single-column for review; flow into the PES Word/LaTeX template for final (Fig.1 at 3.5-in column width, Table captions above, Fig captions below, 8-pt refs).
