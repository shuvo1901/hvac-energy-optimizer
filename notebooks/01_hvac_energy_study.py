"""Research notebook (Jupyter): open in VS Code / Colab.

Run: pip install -r requirements.txt, then execute cells top-to-bottom.
This .py mirror lets GitHub render the workflow without requiring
notebook JSON; the .ipynb in the same folder is the runnable version.
"""
# 1. Generate data
from hvac_optimizer.synthetic import generate_year
df = generate_year(n_days=60)
print(df.describe())

# 2. Forecast
from hvac_optimizer.forecasting import add_time_features, add_lag_features, CoolingLoadForecaster
d = add_lag_features(add_time_features(df), "cooling_load_kw").dropna()
feats = [c for c in d.columns if c != "cooling_load_kw"]
import pandas as pd
feats = [c for c in feats if pd.api.types.is_numeric_dtype(d[c])]
s = int(len(d)*0.8)
fx = CoolingLoadForecaster(model="gbm").fit(d[feats].iloc[:s], d["cooling_load_kw"].iloc[:s])
print(fx.evaluate(d[feats].iloc[s:], d["cooling_load_kw"].iloc[s:]))

# 3. Controls
from hvac_optimizer.optimization import baseline_control, optimize_supply_air_temp
from hvac_optimizer.evaluation import energy_savings_pct
test = d.iloc[s:]
b = baseline_control(test["cooling_load_kw"], test["t_out"])
o = optimize_supply_air_temp(test["cooling_load_kw"], test["t_out"])
print("savings %:", energy_savings_pct(b["p_elec_kw"].sum(), o["p_elec_kw"].sum()))
