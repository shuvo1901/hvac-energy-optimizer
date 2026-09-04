# HVAC Energy Optimizer — Physics-Informed ML for HVAC Systems

[![CI](https://github.com/shuvo1901/Sabbir-Hossain/actions/workflows/ci.yml/badge.svg)](https://github.com/shuvo1901/Sabbir-Hossain/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

By **Sabbir Hossain** · research-grade Python project

Forecast cooling load with gradient boosting, then cut energy with
supply-air-temperature reset, chiller sequencing, and look-ahead pre-cooling —
evaluated with **ASHRAE Guideline 14** metrics.

```
synthetic BMS data → 2R2C thermal model → GBM forecaster → supervisory optimization → kWh + peak savings
```

## Results (synthetic demo, 2000 m² office, Dhaka-like climate)

**Forecast (60-day test):** MAE 1.55 kW · RMSE 2.76 kW · R² 0.9907 ·
CVRMSE 8.30% · NMBE +2.29% — **passes ASHRAE G14** (limits 30% / 10%).

| Strategy | Energy | Saving | Peak | Peak cut |
|---|---|---|---|---|
| Baseline (fixed SAT 13 °C, all chillers on) | 4291.1 kWh (60-d) / 191582.8 kWh (yr) | — | 58.5 kW | — |
| SAT reset 12→16 °C | 3814.5 kWh (60-d) / 165 k MWh (yr) | **11.11%** (13.97% annual) | 54.4 kW | 7.0% |
| Chiller sequencing | 144655.4 kWh (yr) | **24.49%** | 44.0 kW | 24.8% |

Annual bill impact ≈ **$3,211/yr saved** @ $0.12/kWh · **16.1 tCO₂/yr** avoided.
Top load drivers: 168-h lag 45.8% > internal gains 18.4% > occupancy 17.9% > outdoor temp 8.1%.

## Quickstart

```bash
pip install -r requirements.txt
pip install -e .

# 1. generate data (8760 h, seed-reproducible)
python scripts/generate_synthetic_data.py --days 365 --out data/synthetic_hvac.csv

# 2. train + evaluate forecaster (ASHRAE G14 report)
python scripts/train_forecaster.py --csv data/synthetic_hvac.csv --model gbm

# 3. compare controls (energy + peak)
python scripts/evaluate_controls.py --csv data/synthetic_hvac.csv

# 4. full demo → results/metrics.json + results/demo.png
python examples/run_demo.py --days 60 --model gbm

# 5. tests
pytest -q
```

Open `notebooks/01_hvac_energy_study.ipynb` for the full study and
`results/IEEE_PES_HVAC_Paper.pdf` for the two-column conference paper.

## Layout

```
src/hvac_optimizer/   psychrometrics, thermal_model (2R2C + chiller), forecasting,
                      optimization, mpc, evaluation, synthetic, economics
scripts/              generate_synthetic_data, train_forecaster, evaluate_controls,
                      make_pes_twocolumn (paper builder)
examples/run_demo.py  end-to-end pipeline
tests/                pytest suite (5 tests)
docs/                 METHODOLOGY.md, RESEARCH_REPORT.md, CONFERENCE_PAPER.md,
                      IEEE_PES_PAPER.md, IEEE_PES_paper.tex (LaTeX source)
notebooks/            runnable study
results/              metrics.json, demo.png, IEEE_PES_HVAC_Paper.pdf
```

## Physics notes

- Psychrometrics per ASHRAE Fundamentals (Tetens/Magnus, SI units).
- 2R2C zone + PLR/OAT-dependent chiller COP — see `docs/METHODOLOGY.md`.
- Synthetic climate is hot-humid; swap in measured BMS CSV (same column names) for publication.
- Baselines share one part-load curve so only staging/reset effects are measured.

## Citation

```bibtex
@software{hossain2026hvac,
  author  = {Sabbir Hossain},
  title   = {HVAC Energy Optimizer: Physics-Informed ML for HVAC Energy Optimization},
  version = {0.1.0},
  year    = {2026},
  url     = {https://github.com/shuvo1901/Sabbir-Hossain}
}
```

License: MIT — see `LICENSE`.
