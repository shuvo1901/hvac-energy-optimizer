"""Compare baseline / SAT-reset / chiller sequencing on a CSV load profile."""
import argparse, json
import pandas as pd
from hvac_optimizer.optimization import (
    baseline_control, optimize_supply_air_temp, optimize_chiller_sequencing)
from hvac_optimizer.evaluation import energy_savings_pct

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="data/synthetic_hvac.csv")
args = ap.parse_args()
df = pd.read_csv(args.csv, parse_dates=["timestamp"], index_col="timestamp")

base = baseline_control(df["cooling_load_kw"], df["t_out"])
sat = optimize_supply_air_temp(df["cooling_load_kw"], df["t_out"])
seq = optimize_chiller_sequencing(df["cooling_load_kw"], df["t_out"])
eb, es, eq = base["p_elec_kw"].sum(), sat["p_elec_kw"].sum(), seq["p_elec_kw"].sum()
print(json.dumps({
    "kwh_baseline": eb, "kwh_sat_reset": es, "kwh_sequencing": eq,
    "savings_sat_pct": energy_savings_pct(eb, es),
    "savings_seq_pct": energy_savings_pct(eb, eq)}, indent=2))
