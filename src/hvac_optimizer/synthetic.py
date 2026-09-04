"""Synthetic commercial-building dataset generator.

Generates one year (or N days) of hourly data with:
 - Outdoor dry-bulb: seasonal + diurnal + noise (ASHRAE-like hot climate bias)
 - Outdoor RH: anti-correlated with temperature
 - Occupancy: weekday 8-18 schedule with holidays + noise
 - Internal gains: occupants + lighting + equipment
 - Solar gains: bell curve peaking at solar noon, seasonal amplitude
 - Cooling load: physics-flavoured blend of envelope + internal + solar + latent

Output columns match what forecasting.py / optimization.py expect.
Reproducible via --seed (default 42).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_year(
    n_days: int = 365,
    seed: int = 42,
    floor_area_m2: float = 2000.0,
    start: str = "2024-01-01",
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start=start, periods=n_days * 24, freq="h")
    n = len(idx)
    hour = idx.hour.to_numpy()
    dow = idx.dayofweek.to_numpy()
    doy = idx.dayofyear.to_numpy()

    # Outdoor temp: hot-climate city (e.g., Dhaka-like): mean 27, seasonal +-4
    t_season = 27.0 + 4.0 * np.sin(2 * np.pi * (doy - 100) / 365.0)
    t_diurnal = 4.5 * np.sin(2 * np.pi * (hour - 9) / 24.0)
    t_out = t_season + t_diurnal + rng.normal(0, 0.8, n)

    rh_base = 70 - 1.8 * t_diurnal - 0.5 * (t_season - 27.0)
    rh_out = np.clip(rh_base + rng.normal(0, 4, n), 30, 95)

    is_weekday = dow < 5
    # simple holiday mask: ~10 random weekdays off
    holidays = set(rng.choice(np.where(is_weekday)[0], size=10, replace=False))
    is_work = is_weekday & (~np.isin(np.arange(n), list(holidays)))
    occupied = is_work & (hour >= 8) & (hour < 18)
    occ_frac = np.where(
        occupied, np.clip(0.85 + rng.normal(0, 0.08, n), 0.3, 1.0), 0.02
    )

    # Internal gains [kW]: people (130 W/pers sensible+latent equiv) + light/equip
    n_people_peak = floor_area_m2 / 10.0  # 10 m2/person
    q_people = occ_frac * n_people_peak * 0.13
    q_light_equip = floor_area_m2 * (0.012 * (0.3 + 0.7 * occ_frac))
    q_internal = q_people + q_light_equip

    # Solar [kW]: bell around 13:00, seasonal amplitude, zero at night
    solar_noon = np.exp(-0.5 * ((hour - 13.0) / 3.0) ** 2)
    seasonal = 0.7 + 0.3 * np.sin(2 * np.pi * (doy - 80) / 365.0)
    q_solar = floor_area_m2 * 0.015 * solar_noon * np.clip(seasonal, 0.3, 1.0)
    q_solar = q_solar * np.clip(1 + rng.normal(0, 0.15, n), 0.2, 1.4)

    # Envelope + ventilation load [kW]
    ua_kw_per_k = floor_area_m2 * 0.0008  # overall UA
    q_envelope = ua_kw_per_k * np.maximum(t_out - 24.0, 0) * 3.0
    # ventilation latent proxy
    q_latent = occ_frac * n_people_peak * 0.045 * np.clip((rh_out - 50) / 30, 0, 1.2)

    cooling_load = q_internal * 0.9 + q_solar + q_envelope + q_latent
    cooling_load = np.maximum(cooling_load, 0.0)
    cooling_load = cooling_load * np.clip(1 + rng.normal(0, 0.03, n), 0.9, 1.1)

    df = pd.DataFrame(
        {
            "t_out": np.round(t_out, 2),
            "rh_out": np.round(rh_out, 1),
            "occupancy_frac": np.round(occ_frac, 3),
            "is_occupied": occupied.astype(int),
            "q_internal": np.round(q_internal, 2),
            "q_solar": np.round(q_solar, 2),
            "cooling_load_kw": np.round(cooling_load, 2),
        },
        index=idx,
    )
    df.index.name = "timestamp"
    return df


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default="data/synthetic_hvac.csv")
    args = ap.parse_args()
    df = generate_year(n_days=args.days, seed=args.seed)
    df.to_csv(args.out)
    print(f"Wrote {args.out} with shape {df.shape}")
