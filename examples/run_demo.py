"""End-to-end demo: forecast cooling load, compare baseline vs optimized control.

Run:  python examples/run_demo.py --days 60 --model gbm
Outputs: prints metrics + saves figures to results/ + results/metrics.json
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from hvac_optimizer.synthetic import generate_year
from hvac_optimizer.forecasting import (
    add_time_features, add_lag_features, CoolingLoadForecaster,
)
from hvac_optimizer.optimization import baseline_control, optimize_supply_air_temp
from hvac_optimizer.evaluation import energy_savings_pct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--model", type=str, default="gbm", choices=["gbm", "rf", "ridge"])
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = generate_year(n_days=args.days, seed=args.seed)
    df = add_time_features(df)
    df = add_lag_features(df, "cooling_load_kw")
    df = df.dropna().copy()

    feature_cols = [c for c in df.columns if c not in ("cooling_load_kw",)]
    # keep numeric only
    feature_cols = [c for c in feature_cols if pd.api.types.is_numeric_dtype(df[c])]

    split = int(len(df) * 0.8)
    X_train, X_test = df[feature_cols].iloc[:split], df[feature_cols].iloc[split:]
    y_train, y_test = df["cooling_load_kw"].iloc[:split], df["cooling_load_kw"].iloc[split:]

    fx = CoolingLoadForecaster(model=args.model)
    fx.fit(X_train, y_train)
    metrics = fx.evaluate(X_test, y_test)
    print("Forecast metrics:", json.dumps(metrics, indent=2))
    print("Top features:\n", fx.importances().head(10))

    # Controls comparison on test slice (use actual load as perfect forecast upper bound
    # + model forecast as realistic case)
    y_pred = pd.Series(fx.predict(X_test), index=X_test.index)
    base = baseline_control(y_test, X_test["t_out"] if "t_out" in X_test else df["t_out"].iloc[split:])
    opt = optimize_supply_air_temp(y_test, X_test["t_out"] if "t_out" in X_test else df["t_out"].iloc[split:])

    e_base = float(base["p_elec_kw"].sum())
    e_opt = float(opt["p_elec_kw"].sum())
    print(f"Energy baseline={e_base:.1f} kWh  optimized={e_opt:.1f} kWh  "
          f"savings={energy_savings_pct(e_base, e_opt):.2f}%")

    outdir = Path("results")
    outdir.mkdir(exist_ok=True)
    (outdir / "metrics.json").write_text(json.dumps(
        {"forecast": metrics,
         "kwh_baseline": e_base, "kwh_optimized": e_opt,
         "savings_pct": energy_savings_pct(e_base, e_opt)}, indent=2))

    # plots
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax[0].plot(y_test.iloc[:168].values, label="actual load")
    ax[0].plot(y_pred.iloc[:168].values, label="predicted", alpha=0.8)
    ax[0].set_ylabel("kW"); ax[0].legend(); ax[0].set_title("Cooling load: 1-week test slice")
    ax[1].plot(base["p_elec_kw"].iloc[:168].values, label="baseline power")
    ax[1].plot(opt["p_elec_kw"].iloc[:168].values, label="optimized power", alpha=0.8)
    ax[1].set_ylabel("kW"); ax[1].legend(); ax[1].set_title("Power: baseline vs SAT-reset")
    fig.tight_layout(); fig.savefig(outdir / "demo.png", dpi=150)
    print("Saved results/metrics.json + results/demo.png")


if __name__ == "__main__":
    main()
