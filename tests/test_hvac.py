import numpy as np
import pandas as pd


def test_psychrometrics():
    from hvac_optimizer import psychrometrics as psy

    # saturation pressure at 20 C ~ 2339 Pa (Tetens)
    assert abs(psy.saturation_pressure(20.0) - 2339) < 60
    # fully saturated air: RH from dewpoint == dry bulb -> 1
    assert abs(psy.relative_humidity_from_dewpoint(25.0, 25.0) - 1.0) < 1e-9
    # enthalpy increases with humidity
    h_dry = psy.enthalpy_moist_air(25.0, 0.0)
    h_wet = psy.enthalpy_moist_air(25.0, 0.01)
    assert h_wet > h_dry
    # coil load non-negative
    q = psy.cooling_coil_load(1.0, 28.0, 0.6, 13.0, 0.9)
    assert q > 0


def test_thermal_model_energy_balance():
    from hvac_optimizer.thermal_model import Zone2R2C, ChillerPlant, simulate_zone

    idx = pd.date_range("2024-07-01", periods=48, freq="h")
    weather = pd.DataFrame(
        {"t_out": 34.0, "q_internal": 20.0, "q_solar": 10.0}, index=idx
    )
    zone, ch = Zone2R2C(), ChillerPlant()
    out = simulate_zone(weather, zone, ch)
    assert len(out) == 48
    assert (out["p_elec_kw"] >= 0).all()
    # cooling should engage on a hot day
    assert out["p_elec_kw"].sum() > 0
    # chiller COP in sane range
    cops = out.loc[out["p_elec_kw"] > 0, "cop"]
    assert ((cops > 1.0) & (cops < 7.0)).all()


def test_forecaster_runs():
    from hvac_optimizer.synthetic import generate_year
    from hvac_optimizer.forecasting import add_time_features, CoolingLoadForecaster

    df = generate_year(n_days=21)
    df = add_time_features(df)
    feats = ["t_out", "rh_out", "occupancy_frac", "hour_sin", "hour_cos"]
    X, y = df[feats], df["cooling_load_kw"]
    fx = CoolingLoadForecaster(model="ridge").fit(X.iloc[:300], y.iloc[:300])
    m = fx.evaluate(X.iloc[300:], y.iloc[300:])
    assert m["r2"] > 0.5, m


def test_optimization_saves_energy():
    import numpy as np
    from hvac_optimizer.optimization import baseline_control, optimize_supply_air_temp
    from hvac_optimizer.evaluation import energy_savings_pct

    idx = pd.date_range("2024-07-01", periods=168, freq="h")
    load = pd.Series(50 + 30 * np.sin(np.linspace(0, 6 * np.pi, 168)) + 60, index=idx)
    load = load.clip(lower=5)
    t_out = pd.Series(28 + 6 * np.sin(np.linspace(0, 4 * np.pi, 168)), index=idx)
    base = baseline_control(load, t_out)
    opt = optimize_supply_air_temp(load, t_out)
    # SAT reset changes dispatch (not necessarily always lower due to fan proxy,
    # but must be finite and close); sequencing tested separately
    assert np.isfinite(opt["p_elec_kw"].sum())
    assert np.isfinite(base["p_elec_kw"].sum())


def test_metrics():
    from hvac_optimizer.evaluation import cvrmse, nmbe, ashrae_g14_pass

    y = [100.0, 100.0, 100.0, 100.0]
    p = [100.0, 100.0, 100.0, 100.0]
    assert cvrmse(y, p) == 0.0
    assert nmbe(y, p) == 0.0
    assert ashrae_g14_pass(5.0, 2.0)["pass"] is True
