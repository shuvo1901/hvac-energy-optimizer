"""Economics and grid-flexibility helpers (tariff, CO2, peaks, DR potential)."""

from __future__ import annotations

import numpy as np
import pandas as pd

GRID_EF_KG_PER_KWH = 0.6  # Bangladesh grid proxy


def annual_bill(kwh: float, tariff_per_kwh: float = 0.12) -> float:
    return float(kwh) * float(tariff_per_kwh)


def co2_tonnes(kwh: float, ef: float = GRID_EF_KG_PER_KWH) -> float:
    return float(kwh) * float(ef) / 1000.0


def peak_kw(power: pd.Series | np.ndarray) -> float:
    return float(np.max(np.asarray(power, dtype=float)))


def flexibility_offer(baseline_kw, optimized_kw) -> dict:
    """Average / peak sheddable kW and shifted kWh proxy."""
    b = np.asarray(baseline_kw, dtype=float)
    o = np.asarray(optimized_kw, dtype=float)
    shed = np.maximum(b - o, 0.0)
    return {
        "avg_shed_kw": float(shed.mean()),
        "peak_shed_kw": float(shed.max()),
        "shifted_kwh": float(shed.sum()),
    }
