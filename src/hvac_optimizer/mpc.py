"""Simplified receding-horizon MPC for pre-cooling demonstration.

Full MPC (CasADi/pyomo) is out of scope for a zero-solver dependency
package; this greedy look-ahead controller captures the core research
idea -- shift load to high-COP (cool night) hours within comfort bounds --
and is directly comparable against the baseline in examples/.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class SimpleMPC:
    """Look-ahead pre-cooling controller.

    At each step, if a high-OAT (low-COP) period is coming within
    `horizon_h` and the zone is currently above `t_precool`, apply extra
    cooling now (up to `max_cool_kw`) so later peak load is reduced.
    Comfort is enforced as t_in within [t_min, t_max].
    """

    def __init__(
        self,
        horizon_h: int = 4,
        t_min: float = 22.0,
        t_max: float = 25.5,
        t_precool: float = 23.0,
        oat_threshold: float = 32.0,
        max_cool_kw: float = 200.0,
    ):
        self.horizon_h = horizon_h
        self.t_min = t_min
        self.t_max = t_max
        self.t_precool = t_precool
        self.oat_threshold = oat_threshold
        self.max_cool_kw = max_cool_kw

    def plan_step(
        self,
        t_in_now: float,
        t_out_future: np.ndarray,
        load_forecast_kw: np.ndarray,
    ) -> float:
        """Return cooling power [kW, >=0] to apply this step."""
        peak_ahead = bool(
            np.any(np.asarray(t_out_future[: self.horizon_h]) >= self.oat_threshold)
        )
        load_now = float(load_forecast_kw[0]) if len(load_forecast_kw) else 0.0
        if peak_ahead and t_in_now > self.t_min + 0.2:
            # pre-cool proportionally to upcoming load
            upcoming = float(np.mean(load_forecast_kw[: self.horizon_h])) if len(
                load_forecast_kw
            ) else 0.0
            extra = min(self.max_cool_kw * 0.6, max(0.0, upcoming - load_now) + 20.0)
            base = min(self.max_cool_kw, max(0.0, load_now))
            return float(min(self.max_cool_kw, base + extra))
        # normal tracking: meet current load if warm
        if t_in_now > self.t_precool:
            return float(min(self.max_cool_kw, max(0.0, load_now)))
        return 0.0

    def simulate(
        self,
        df: pd.DataFrame,
        load_col: str = "cooling_load_kw",
        t_out_col: str = "t_out",
        t_in_init: float = 24.0,
        thermal_mass_factor: float = 0.15,
    ) -> pd.DataFrame:
        """Closed-loop simulation on a dataframe with load + OAT columns.

        thermal_mass_factor converts excess pre-cooling [kWh] into zone
        temperature depression [K/kWh] -- a deliberately simple proxy so
        the energy-shifting benefit is visible without a full RC co-sim.
        """
        n = len(df)
        load = df[load_col].to_numpy(dtype=float)
        t_out = df[t_out_col].to_numpy(dtype=float)
        t_in = np.zeros(n)
        q_cool = np.zeros(n)
        ti = t_in_init
        for i in range(n):
            fut_t = t_out[i : i + self.horizon_h]
            fut_l = load[i : i + self.horizon_h]
            # pad at tail
            if len(fut_t) < self.horizon_h:
                pad = self.horizon_h - len(fut_t)
                fut_t = np.pad(fut_t, (0, pad), constant_values=fut_t[-1] if len(fut_t) else 30)
                fut_l = np.pad(fut_l, (0, pad), constant_values=fut_l[-1] if len(fut_l) else 0)
            q = self.plan_step(ti, fut_t, fut_l)
            q_cool[i] = q
            # simple zone response: cooling drives toward t_min, internal gains drift up
            excess = q - load[i]
            ti = ti - excess * thermal_mass_factor * 0.1 + 0.02 * (t_out[i] - ti) * 0.1
            ti = float(np.clip(ti, self.t_min - 0.5, self.t_max + 1.0))
            t_in[i] = ti
        return pd.DataFrame({"t_in": t_in, "q_cool_kw": q_cool}, index=df.index)
