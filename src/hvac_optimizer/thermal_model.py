"""Lumped-capacitance building thermal model (2R2C) + chiller plant model.

The 2R2C zone model is standard in MPC / system-ID literature:

    C_in dT_in/dt  = (T_wall - T_in)/R_in + Q_int + Q_solar_win + Q_hvac
    C_wall dT_wall/dt = (T_out - T_wall)/R_out + (T_in - T_wall)/R_in

Q_hvac is negative for cooling. Integrated with explicit Euler at
configurable dt (default 1 h to match hourly energy data, but any
dt works if inputs are per-step energies/powers handled consistently).

Units: T in degC, R in K/kW, C in kWh/K, Q in kW, dt in hours.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Zone2R2C:
    """2R2C zone parameters."""

    R_in: float = 1.5  # K/kW, indoor air <-> wall mass
    R_out: float = 2.5  # K/kW, wall mass <-> outdoor
    C_in: float = 2.0  # kWh/K, indoor air + furniture
    C_wall: float = 8.0  # kWh/K, envelope mass
    t_in_init: float = 24.0
    t_wall_init: float = 24.0

    def step(self, t_in, t_wall, t_out, q_int_kw, q_hvac_kw, dt_h=1.0):
        """Advance one timestep. Returns (t_in_next, t_wall_next)."""
        d_t_in = (
            (t_wall - t_in) / self.R_in + q_int_kw + q_hvac_kw
        ) * dt_h / self.C_in
        d_t_wall = (
            (t_out - t_wall) / self.R_out + (t_in - t_wall) / self.R_in
        ) * dt_h / self.C_wall
        return t_in + d_t_in, t_wall + d_t_wall


@dataclass
class ChillerPlant:
    """Simple water-cooled chiller: COP varies with part-load ratio (PLR) and OAT.

    COP = COP_rated * (a + b*PLR + c*PLR^2) * (1 - k*(T_cond - T_cond_rated))
    with T_cond approximated from outdoor dry-bulb. This captures the two
    first-order effects needed for sequencing / setpoint studies without
    a full Gordon-Ng model.
    """

    capacity_kw: float = 350.0
    cop_rated: float = 3.5
    n_chillers: int = 2
    plr_min: float = 0.15

    def cop(self, load_kw, t_out_c) -> float:
        """Instantaneous COP for a given total plant load and OAT."""
        load_kw = max(float(load_kw), 0.0)
        if load_kw <= 0:
            return self.cop_rated
        # split evenly across committed chillers (simple sequencing)
        per = load_kw / self.n_chillers
        cap_each = self.capacity_kw / self.n_chillers
        plr = float(np.clip(per / max(cap_each, 1e-9), 0.0, 1.0))
        # part-load curve (typical screw chiller shape)
        f_plr = 0.45 + 0.85 * plr - 0.30 * plr**2
        # condenser penalty: ~1.2%/K above 35 C rating point
        f_oat = 1.0 - 0.012 * (float(t_out_c) - 35.0)
        f_oat = float(np.clip(f_oat, 0.6, 1.15))
        return max(0.5, self.cop_rated * f_plr * f_oat)

    def power(self, load_kw, t_out_c) -> float:
        """Electric power [kW] for a cooling load [kW]."""
        if load_kw <= 0:
            return 0.0
        return float(load_kw) / max(self.cop(load_kw, t_out_c), 1e-6)


def simulate_zone(
    weather: pd.DataFrame,
    zone: Zone2R2C,
    chiller: ChillerPlant,
    t_set_cool: float = 24.0,
    t_setback: float = 28.0,
    occupied_mask=None,
    max_cool_kw: float = 200.0,
    dt_h: float = 1.0,
) -> pd.DataFrame:
    """Run a deadband on/off + proportional cooling simulation.

    Parameters
    ----------
    weather : DataFrame with columns ['t_out', 'q_internal', 'q_solar'] in
        degC / kW / kW, indexed by timestamp.
    occupied_mask : bool array; when False the setback setpoint applies.

    Returns DataFrame with ['t_in','t_wall','q_hvac_kw','p_elec_kw','cop'].
    """
    n = len(weather)
    if occupied_mask is None:
        occupied = np.ones(n, dtype=bool)
    else:
        occupied = np.asarray(occupied_mask, dtype=bool)

    t_in = np.zeros(n)
    t_wall = np.zeros(n)
    q_hvac = np.zeros(n)
    p_elec = np.zeros(n)
    cops = np.zeros(n)

    ti, tw = zone.t_in_init, zone.t_wall_init
    for i in range(n):
        t_out = float(weather["t_out"].iloc[i])
        q_int = float(weather["q_internal"].iloc[i]) + float(
            weather["q_solar"].iloc[i]
        )
        sp = t_set_cool if occupied[i] else t_setback
        # proportional control capped at max_cool_kw
        err = ti - sp
        if err > 0:
            q_cmd = -min(max_cool_kw, 8.0 * err)  # 8 kW/K gain
        else:
            q_cmd = 0.0
        cool_kw = -q_cmd
        p = chiller.power(cool_kw, t_out)
        c = chiller.cop(cool_kw, t_out) if cool_kw > 0 else 0.0

        ti_next, tw_next = zone.step(ti, tw, t_out, q_int, q_cmd, dt_h)
        t_in[i], t_wall[i] = ti_next, tw_next
        q_hvac[i], p_elec[i], cops[i] = q_cmd, p, c
        ti, tw = ti_next, tw_next

    out = pd.DataFrame(
        {
            "t_in": t_in,
            "t_wall": t_wall,
            "q_hvac_kw": q_hvac,
            "p_elec_kw": p_elec,
            "cop": cops,
        },
        index=weather.index,
    )
    return out
