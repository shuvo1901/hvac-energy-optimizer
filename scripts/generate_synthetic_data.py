"""Generate synthetic HVAC dataset (CLI wrapper)."""
import argparse
from pathlib import Path
from hvac_optimizer.synthetic import generate_year

ap = argparse.ArgumentParser(description="Generate synthetic HVAC data")
ap.add_argument("--days", type=int, default=365)
ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--area", type=float, default=2000.0)
ap.add_argument("--out", type=str, default="data/synthetic_hvac.csv")
args = ap.parse_args()

df = generate_year(n_days=args.days, seed=args.seed, floor_area_m2=args.area)
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
df.to_csv(args.out)
print(f"Wrote {args.out} shape={df.shape} load_mean={df['cooling_load_kw'].mean():.1f} kW")
