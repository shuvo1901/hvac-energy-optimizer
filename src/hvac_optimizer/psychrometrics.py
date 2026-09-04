"""Psychrometric functions per ASHRAE Fundamentals (SI units).

All temperatures in degC unless noted, pressure in Pa, enthalpy in J/kg-da.
References: ASHRAE Handbook Fundamentals Ch.1, Tetens (1930) for
saturation pressure, Magnus formula for dew point.
"""

from __future__ import annotations

import numpy as np

P_ATM = 101325.0  # Pa


def _as_array(x):
    return np.asarray(x, dtype=float)


def saturation_pressure(t_db_c) -> np.ndarray | float:
    """Saturation pressure over water (Pa) for dry-bulb temp in degC.

    Uses Tetens equation, valid -40..50 C, error < 1% vs Hyland-Wexler
    in HVAC range. Good default for research code without CoolProp.
    """
    t = _as_array(t_db_c)
    # Tetens: 610.78 * exp(17.27*T / (T+237.3))
    psat = 610.78 * np.exp(17.27 * t / (t + 237.3))
    return float(psat) if psat.ndim == 0 else psat


def humidity_ratio(t_db_c, rh, p_atm: float = P_ATM) -> np.ndarray | float:
    """Humidity ratio W [kg-w/kg-da] from dry-bulb (C) and RH (0-1)."""
    t = _as_array(t_db_c)
    rh_a = np.clip(_as_array(rh), 0.0, 1.0)
    psat = saturation_pressure(t)
    pv = rh_a * psat
    w = 0.621945 * pv / (p_atm - pv)
    return float(w) if np.ndim(w) == 0 else w


def relative_humidity_from_dewpoint(t_db_c, t_dew_c) -> np.ndarray | float:
    """RH (0-1) from dry-bulb and dew-point temperatures (C)."""
    psat_db = saturation_pressure(_as_array(t_db_c))
    psat_dew = saturation_pressure(_as_array(t_dew_c))
    rh = np.clip(psat_dew / np.maximum(psat_db, 1e-9), 0.0, 1.0)
    return float(rh) if np.ndim(rh) == 0 else rh


def dew_point(t_db_c, rh) -> np.ndarray | float:
    """Dew-point temperature (C) from dry-bulb (C) and RH (0-1). Magnus formula."""
    rh_a = np.clip(_as_array(rh), 0.01, 1.0)
    t = _as_array(t_db_c)
    a, b = 17.27, 237.7
    alpha = np.log(rh_a) + (a * t) / (b + t)
    t_dew = (b * alpha) / (a - alpha)
    return float(t_dew) if np.ndim(t_dew) == 0 else t_dew


def enthalpy_moist_air(t_db_c, w) -> np.ndarray | float:
    """Specific enthalpy of moist air [J/kg-da]: h = 1.006*T + W*(2501+1.86*T), T in C."""
    t = _as_array(t_db_c)
    w_a = _as_array(w)
    h_kj = 1.006 * t + w_a * (2501.0 + 1.86 * t)  # kJ/kg-da
    h = h_kj * 1000.0
    return float(h) if np.ndim(h) == 0 else h


def moist_air_density(t_db_c, rh, p_atm: float = P_ATM) -> np.ndarray | float:
    """Moist air density [kg/m3] via ideal gas mixture."""
    t = _as_array(t_db_c)
    w = humidity_ratio(t, rh, p_atm)
    t_k = t + 273.15
    # density of dry air + vapor approx: p/(R*T) corrected
    r_da, r_wv = 287.058, 461.495
    pv = np.clip(_as_array(rh), 0, 1) * saturation_pressure(t)
    p_da = p_atm - pv
    rho = p_da / (r_da * t_k) + pv / (r_wv * t_k)
    void = w  # keep linter calm about unused
    del void
    return float(rho) if np.ndim(rho) == 0 else rho


def cooling_coil_load(
    m_dot_da: float | np.ndarray,
    t_in_c,
    rh_in,
    t_out_c,
    rh_out,
) -> np.ndarray | float:
    """Sensible+latent coil load [W] = m_dot_da * (h_in - h_out), clipped at >= 0."""
    w_in = humidity_ratio(t_in_c, rh_in)
    w_out = humidity_ratio(t_out_c, rh_out)
    h_in = enthalpy_moist_air(t_in_c, w_in)
    h_out = enthalpy_moist_air(t_out_c, w_out)
    q = np.asarray(m_dot_da, dtype=float) * (np.asarray(h_in) - np.asarray(h_out))
    q = np.maximum(q, 0.0)
    return float(q) if np.ndim(q) == 0 else q
