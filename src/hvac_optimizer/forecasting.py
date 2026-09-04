"""Cooling-load forecasting with calendar + weather features.

Research default: GradientBoostingRegressor (no extra deps beyond
scikit-learn). Time features are cyclical (sin/cos) to avoid the
midnight discontinuity that hurts tree/linear models.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit, cross_val_score


def add_time_features(df: pd.DataFrame, timestamp_col: str | None = None) -> pd.DataFrame:
    """Add hour/dayofweek/month cyclical features + lags placeholder.

    If timestamp_col is given, use that column; otherwise use the index.
    """
    out = df.copy()
    if timestamp_col is not None:
        ts = pd.to_datetime(out[timestamp_col])
    else:
        ts = pd.to_datetime(out.index)
    hour = ts.hour.to_numpy() if hasattr(ts, "hour") else ts.map(lambda x: x.hour)
    dow = (
        ts.dayofweek.to_numpy()
        if hasattr(ts, "dayofweek")
        else ts.map(lambda x: x.dayofweek)
    )
    month = ts.month.to_numpy() if hasattr(ts, "month") else ts.map(lambda x: x.month)
    hour = np.asarray(hour, dtype=float)
    dow = np.asarray(dow, dtype=float)
    month = np.asarray(month, dtype=float)

    out["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
    out["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
    out["dow_sin"] = np.sin(2 * np.pi * dow / 7.0)
    out["dow_cos"] = np.cos(2 * np.pi * dow / 7.0)
    out["month_sin"] = np.sin(2 * np.pi * (month - 1) / 12.0)
    out["month_cos"] = np.cos(2 * np.pi * (month - 1) / 12.0)
    out["is_weekend"] = (dow >= 5).astype(int)
    out["is_occupied_hour"] = (
        ((hour >= 8) & (hour < 18) & (dow < 5)).astype(int)
    )
    return out


def add_lag_features(
    df: pd.DataFrame, target: str, lags: tuple[int, ...] = (1, 24, 168)
) -> pd.DataFrame:
    """Add lagged target features (rows with NaN must be dropped by caller)."""
    out = df.copy()
    for lag in lags:
        out[f"{target}_lag{lag}"] = out[target].shift(lag)
    return out


class CoolingLoadForecaster:
    """Thin wrapper so notebooks/paper share one training path."""

    def __init__(self, model: str = "gbm", random_state: int = 42, **kwargs):
        if model == "gbm":
            self.model = GradientBoostingRegressor(random_state=random_state, **kwargs)
        elif model == "rf":
            self.model = RandomForestRegressor(
                n_estimators=200, random_state=random_state, n_jobs=-1, **kwargs
            )
        elif model == "ridge":
            self.model = Ridge(**kwargs)
        else:
            raise ValueError(f"Unknown model={model!r}; choose gbm/rf/ridge")
        self.feature_names_: list[str] | None = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.feature_names_ = list(X.columns)
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.asarray(self.model.predict(X))

    def evaluate(self, X, y) -> dict:
        pred = self.predict(X)
        y_a = np.asarray(y, dtype=float)
        rmse = float(np.sqrt(mean_squared_error(y_a, pred)))
        mean = float(np.mean(y_a)) if len(y_a) else 0.0
        return {
            "mae": float(mean_absolute_error(y_a, pred)),
            "rmse": rmse,
            "cvrmse_pct": float(rmse / abs(mean) * 100.0) if mean else float("inf"),
            "nmbe_pct": float(
                np.sum(y_a - pred) / ((len(y_a) - 1) * mean) * 100.0
            )
            if mean
            else float("inf"),
            "r2": float(r2_score(y_a, pred)) if len(set(y_a)) > 1 else 0.0,
        }

    def time_series_cv(self, X, y, n_splits: int = 5) -> dict:
        tscv = TimeSeriesSplit(n_splits=n_splits)
        scores = cross_val_score(
            self.model, X, y, cv=tscv, scoring="neg_root_mean_squared_error"
        )
        return {"rmse_mean": float(-scores.mean()), "rmse_std": float(scores.std())}

    def importances(self) -> pd.Series:
        if hasattr(self.model, "feature_importances_"):
            vals = self.model.feature_importances_
        elif hasattr(self.model, "coef_"):
            vals = np.abs(np.asarray(self.model.coef_).ravel())
        else:
            raise AttributeError("Model has no importances/coef_")
        idx = self.feature_names_ or [f"f{i}" for i in range(len(vals))]
        return pd.Series(vals, index=idx).sort_values(ascending=False)
