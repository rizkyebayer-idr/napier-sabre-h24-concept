# -*- coding: utf-8 -*-
"""Steady-state fuel consumption, eq. (7)."""
from __future__ import annotations

from typing import Optional, Tuple

from . import dynamics, engine
from . import params as p


def consumption_at_speed(v_kmh: float) -> Tuple[float, float, int]:
    """Best-gear steady-state consumption.

    For each gear the engine speed must lie within [FUEL_MIN_RPM, SHIFT_RPM];
    the gear giving the lowest fuel flow is selected.

    Returns (L/100 km, engine speed rpm, gear index).
    """
    v = v_kmh / 3.6
    best = (float("inf"), float("nan"), -1)
    for g in range(len(p.GEAR_RATIOS)):
        n = dynamics.engine_speed_rpm(v, g)
        if not (p.FUEL_MIN_RPM <= n <= p.SHIFT_RPM):
            continue
        pb = dynamics.brake_power_demand_W(v)
        mdot = engine.fuel_flow_kgs(n, pb)
        litres_per_100km = mdot * (100_000.0 / v) / p.RHO_FUEL
        if litres_per_100km < best[0]:
            best = (litres_per_100km, n, g)
    return best


def idle_litres_per_hour() -> float:
    """Fuel burned at the minimum idle speed [L/h]."""
    mdot = engine.fuel_flow_kgs(p.IDLE_RPM, 0.0)
    return mdot * 3600.0 / p.RHO_FUEL


def full_power_litres_per_hour() -> float:
    """Fuel burned at rated power, from full-load BSFC [L/h]."""
    return engine.fuel_flow_full_power_kgh() / p.RHO_FUEL


def curve(v_from=20.0, v_to=320.0, step=2.0):
    """Steady-state consumption curve for plotting."""
    out = []
    v = v_from
    while v <= v_to:
        lp100, n, g = consumption_at_speed(v)
        if g >= 0:
            out.append((v, lp100, n, g))
        v += step
    return out
