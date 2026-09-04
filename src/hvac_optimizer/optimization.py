"""Supervisory optimization strategies for HVAC energy reduction.

Three layers (research framing):
  1. baseline_control -- fixed setpoint, fixed supply-air temp (business as usual).
  2. optimize_supply_air_temp -- reset SAT with OAT (warmest SAT that still
     meets the load); fan + chiller trade-off approximated.
  3. optimize_chiller_sequencing -- commit minimum chillers for a load.
  4. (see mpc.py) receding-horizon pre-cooling.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def baseline_control(
    load_kw: pd.Series | np.ndarray,
    t_out,
    sat_c: float = 13.0,
    cop_rated: float = 3.5,
    capacity_each_kw: float = 175.0,
    n_max: int = 2,
) -> pd.DataFrame:
    """Fixed-SAT baseline: all chillers committed (business as usual).

    Includes the same part-load curve as the sequencing model so the
    comparison is fair: baseline splits load across ALL n_max chillers,
    optimized commits the minimum. Constant-speed fan proxy included.
    """
    load = np.asarray(load_kw, dtype=float)
    t_out_a = np.asarray(t_out, dtype=float)
    cap_total = max(n_max * capacity_each_kw, 1e-9)
    plr = np.clip(load / cap_total, 0, 1.0)
    f_plr = 0.45 + 0.85 * plr - 0.30 * plr**2
    f_oat = np.clip(1.0 - 0.012 * (t_out_a - 35.0), 0.6, 1.15)
    cop = np.clip(cop_rated * f_plr * f_oat, 0.5, 5.0)
    cop = np.where(load > 1e-6, cop, cop_rated)
    p_chiller = np.where(load > 0, load / np.maximum(cop, 1e-6), 0.0)
    # constant-volume fan: ~2% of peak load as electric proxy
    peak = float(load.max()) if load.size else 0.0
    p_fan = np.where(load > 0, 0.02 * peak, 0.0)
    p = p_chiller + p_fan
    idx = load_kw.index if isinstance(load_kw, pd.Series) else None
    return pd.DataFrame(
        {"p_elec_kw": p, "p_chiller_kw": p_chiller, "p_fan_kw": p_fan,
         "cop": cop, "sat_c": sat_c},
        index=idx,
    )


def optimize_supply_air_temp(
    load_kw,
    t_out,
    t_zone_c: float = 24.0,
    sat_min: float = 12.0,
    sat_max: float = 16.0,
    cop_rated: float = 3.5,
) -> pd.DataFrame:
    """OAT-reset of supply-air temperature.

    Higher SAT at mild OAT saves chiller lift + reheat at the cost of
    slightly higher fan energy. Fan penalty modelled as cubic in airflow,
    airflow inversely proportional to (T_zone - SAT).
    """
    load = np.asarray(load_kw, dtype=float)
    t_out_a = np.asarray(t_out, dtype=float)
    # reset schedule: coldest SAT at hot OAT
    sat = sat_max - (np.clip(t_out_a, 18, 38) - 18) / (38 - 18) * (sat_max - sat_min)
    sat = np.clip(sat, sat_min, sat_max)
    dT = np.maximum(t_zone_c - sat, 1.0)
    # VAV fan proxy: slightly higher flow at high SAT, cubic law
    flow_ratio = np.clip((load / np.maximum(load.max(), 1e-9)) * (4.0 / dT), 0, 1.5)
    p_fan = 0.025 * load.max() * flow_ratio**3 if load.max() > 0 else np.zeros_like(load)
    # chiller: same part-load curve as baseline + modest SAT lift benefit (~2%)
    cap_total = 350.0
    plr = np.clip(load / cap_total, 0, 1.0)
    f_plr = 0.45 + 0.85 * plr - 0.30 * plr**2
    f_oat = np.clip(1.0 - 0.010 * (t_out_a - 35.0), 0.6, 1.15)
    cop = np.clip(cop_rated * f_plr * f_oat * 1.02, 0.5, 5.2)
    cop = np.where(load > 1e-6, cop, cop_rated)
    p_chiller = np.where(load > 0, load / cop, 0.0)
    p_total = p_chiller + p_fan
    idx = load_kw.index if isinstance(load_kw, pd.Series) else None
    return pd.DataFrame(
        {"p_elec_kw": p_total, "p_chiller_kw": p_chiller, "p_fan_kw": p_fan,
         "cop": cop, "sat_c": sat},
        index=idx,
    )


def optimize_chiller_sequencing(
    load_kw,
    t_out,
    capacity_each_kw: float = 175.0,
    n_max: int = 2,
    cop_rated: float = 3.5,
) -> pd.DataFrame:
    """Commit fewest chillers that meet load above minimum PLR; split evenly."""
    load = np.asarray(load_kw, dtype=float)
    t_out_a = np.asarray(t_out, dtype=float)
    n_commit = np.zeros_like(load, dtype=int)
    cop = np.zeros_like(load, dtype=float)
    p = np.zeros_like(load, dtype=float)
    for i, (ld, to) in enumerate(zip(load, t_out_a)):
        if ld <= 1e-6:
            continue
        # try 1..n_max chillers, pick best COP
        best_p, best_c, best_n = float("inf"), cop_rated, 1
        for n in range(1, n_max + 1):
            cap = n * capacity_each_kw
            if ld > cap:
                continue
            plr = (ld / n) / capacity_each_kw
            if plr < 0.15:
                continue
            f_plr = 0.45 + 0.85 * plr - 0.30 * plr**2
            f_oat = np.clip(1.0 - 0.012 * (to - 35.0), 0.6, 1.15)
            c = max(0.5, cop_rated * f_plr * f_oat)
            pp = ld / c
            if pp < best_p:
                best_p, best_c, best_n = pp, c, n
        if best_p == float("inf"):  # load exceeds plant or tiny -> run all
            best_n = n_max
            plr = (ld / n_max) / capacity_each_kw
            f_plr = 0.45 + 0.85 * min(plr, 1.0) - 0.30 * min(plr, 1.0) ** 2
            best_c = max(0.5, cop_rated * f_plr)
            best_p = ld / best_c
        n_commit[i], cop[i], p[i] = best_n, best_c, best_p
    idx = load_kw.index if isinstance(load_kw, pd.Series) else None
    return pd.DataFrame(
        {"p_elec_kw": p, "cop": cop, "n_chillers": n_commit}, index=idx
    )
