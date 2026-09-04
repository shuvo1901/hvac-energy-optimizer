"""Train forecaster on CSV and report ASHRAE G14 metrics."""
import argparse, json
import pandas as pd
from hvac_optimizer.forecasting import add_time_features, add_lag_features, CoolingLoadForecaster
from hvac_optimizer.evaluation import ashrae_g14_pass

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="data/synthetic_hvac.csv")
ap.add_argument("--target", default="cooling_load_kw")
ap.add_argument("--model", default="gbm", choices=["gbm", "rf", "ridge"])
args = ap.parse_args()

df = pd.read_csv(args.csv, parse_dates=["timestamp"], index_col="timestamp")
df = add_time_features(df)
df = add_lag_features(df, args.target).dropna()
feats = [c for c in df.columns if c != args.target and pd.api.types.is_numeric_dtype(df[c])]
s = int(len(df) * 0.8)
fx = CoolingLoadForecaster(model=args.model).fit(df[feats].iloc[:s], df[args.target].iloc[:s])
m = fx.evaluate(df[feats].iloc[s:], df[args.target].iloc[s:])
m["ashrae_g14"] = ashrae_g14_pass(m["cvrmse_pct"], m["nmbe_pct"])
print(json.dumps(m, indent=2))
