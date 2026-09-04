"""Evaluation metrics incl. ASHRAE Guideline 14 calibration metrics."""

from __future__ import annotations

import numpy as np


def _a(y_true, y_pred):
    return np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)


def mae(y_true, y_pred) -> float:
    yt, yp = _a(y_true, y_pred)
    return float(np.mean(np.abs(yt - yp)))


def rmse(y_true, y_pred) -> float:
    yt, yp = _a(y_true, y_pred)
    return float(np.sqrt(np.mean((yt - yp) ** 2)))


def cvrmse(y_true, y_pred) -> float:
    """Coefficient of Variation of RMSE [%], ASHRAE G14: RMSE/mean(y)*100."""
    yt, yp = _a(y_true, y_pred)
    mean = float(np.mean(yt))
    if abs(mean) < 1e-12:
        return float("inf")
    return float(np.sqrt(np.mean((yt - yp) ** 2)) / abs(mean) * 100.0)


def nmbe(y_true, y_pred) -> float:
    """Normalized Mean Bias Error [%], ASHRAE G14: sum(yt-yp)/((n-p)*mean)*100, p=1."""
    yt, yp = _a(y_true, y_pred)
    mean = float(np.mean(yt))
    if abs(mean) < 1e-12:
        return float("inf")
    return float(np.sum(yt - yp) / ((len(yt) - 1) * mean) * 100.0)


def r2_score_safe(y_true, y_pred) -> float:
    yt, yp = _a(y_true, y_pred)
    ss_res = float(np.sum((yt - yp) ** 2))
    ss_tot = float(np.sum((yt - np.mean(yt)) ** 2))
    if ss_tot < 1e-12:
        return 0.0
    return float(1.0 - ss_res / ss_tot)


def energy_savings_pct(baseline_kwh: float, optimized_kwh: float) -> float:
    if baseline_kwh <= 0:
        return 0.0
    return float((baseline_kwh - optimized_kwh) / baseline_kwh * 100.0)


def ashrae_g14_pass(cvrmse_val: float, nmbe_val: float, hourly: bool = True) -> dict:
    """Check ASHRAE Guideline 14 hourly/monthly calibration limits."""
    lim_cvr = 30.0 if hourly else 15.0
    lim_nmb = 10.0 if hourly else 5.0
    return {
        "cvrmse_limit": lim_cvr,
        "nmbe_limit": lim_nmb,
        "cvrmse_pass": abs(cvrmse_val) <= lim_cvr,
        "nmbe_pass": abs(nmbe_val) <= lim_nmb,
        "pass": abs(cvrmse_val) <= lim_cvr and abs(nmbe_val) <= lim_nmb,
    }
