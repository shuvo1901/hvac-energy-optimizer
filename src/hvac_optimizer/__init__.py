"""HVAC Energy Optimizer: physics-informed ML for HVAC energy optimization."""

from hvac_optimizer.psychrometrics import (
    saturation_pressure,
    humidity_ratio,
    enthalpy_moist_air,
    dew_point,
    relative_humidity_from_dewpoint,
)
from hvac_optimizer.thermal_model import Zone2R2C, ChillerPlant, simulate_zone
from hvac_optimizer.forecasting import CoolingLoadForecaster, add_time_features
from hvac_optimizer.optimization import (
    optimize_supply_air_temp,
    optimize_chiller_sequencing,
    baseline_control,
)
from hvac_optimizer.evaluation import (
    mae,
    rmse,
    cvrmse,
    nmbe,
    r2_score_safe,
    energy_savings_pct,
)
from hvac_optimizer.mpc import SimpleMPC

__all__ = [
    "saturation_pressure",
    "humidity_ratio",
    "enthalpy_moist_air",
    "dew_point",
    "relative_humidity_from_dewpoint",
    "Zone2R2C",
    "ChillerPlant",
    "simulate_zone",
    "CoolingLoadForecaster",
    "add_time_features",
    "optimize_supply_air_temp",
    "optimize_chiller_sequencing",
    "baseline_control",
    "mae",
    "rmse",
    "cvrmse",
    "nmbe",
    "r2_score_safe",
    "energy_savings_pct",
    "SimpleMPC",
]

__version__ = "0.1.0"
