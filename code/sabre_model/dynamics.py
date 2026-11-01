# -*- coding: utf-8 -*-
"""
Longitudinal dynamics: road load, traction limits, top speed, acceleration.

Default arguments that depend on params are resolved at call time (not at import
time) so that the sensitivity study can vary them.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from . import engine
from . import params as p

G = 9.81


def _m(mass: Optional[float]) -> float:
    return p.MASS_KG if mass is None else mass


def road_load_N(v: float, mass: Optional[float] = None) -> float:
    """Road-load resistance, eq. (3): aero drag plus rolling resistance."""
    m = _m(mass)
    return 0.5 * p.RHO_AIR * p.CD * p.FRONTAL_AREA * v * v + p.C_RR * m * G


def road_load_power_W(v: float, mass: Optional[float] = None) -> float:
    return road_load_N(v, mass) * v


def brake_power_demand_W(v: float, mass: Optional[float] = None) -> float:
    return road_load_power_W(v, mass) / p.ETA_DRIVELINE


def traction_limit_N(ax: float = 0.0, mass: Optional[float] = None,
                     cg_x: Optional[float] = None, cg_z: Optional[float] = None,
                     mu: Optional[float] = None) -> float:
    """Max rear-tyre force incl. longitudinal load transfer, eq. (5).

        Fx,max = mu ( m g lf / L + m ax h / L )
    """
    m = _m(mass)
    x = p.CG_X if cg_x is None else cg_x
    z = p.CG_Z if cg_z is None else cg_z
    f = p.MU if mu is None else mu
    return f * (m * G * x / p.WHEELBASE + m * ax * z / p.WHEELBASE)


def traction_limit_dynamic_N(mass: Optional[float] = None,
                             cg_x: Optional[float] = None,
                             cg_z: Optional[float] = None,
                             mu: Optional[float] = None) -> float:
    """Traction limit with load transfer, solved self-consistently.

    Eq. (5) makes the limit depend on the acceleration it produces, so both are
    solved together:

        Fx = mu m g lf / L + mu h / L * (Fx - FR) / (k m)
    """
    m = _m(mass)
    x = p.CG_X if cg_x is None else cg_x
    z = p.CG_Z if cg_z is None else cg_z
    f = p.MU if mu is None else mu
    a_term = f * m * G * x / p.WHEELBASE
    b_term = f * z / (p.WHEELBASE * p.ROT_MASS_FACTOR)
    return (a_term - b_term * road_load_N(0.0, m)) / (1.0 - b_term)


def engine_speed_rpm(v: float, gear: int) -> float:
    return v / p.R_TYRE * p.GEAR_RATIOS[gear] * 60.0 / (2.0 * math.pi)


def road_speed_ms(n_rpm: float, gear: int) -> float:
    return n_rpm * 2.0 * math.pi / 60.0 / p.GEAR_RATIOS[gear] * p.R_TYRE


def gear_top_speeds_kmh(n_rpm: Optional[float] = None) -> List[float]:
    n = p.SHIFT_RPM if n_rpm is None else n_rpm
    return [road_speed_ms(n, g) * 3.6 for g in range(len(p.GEAR_RATIOS))]


def tractive_force_N(v: float, gear: int) -> float:
    """Force at the driven wheels in the given gear, eq. (2).

    Below the launch speed the clutch slips, so the engine can still deliver
    torque; above the rated speed the curve follows the power hyperbola.
    """
    ratio = p.GEAR_RATIOS[gear]
    n = max(engine_speed_rpm(v, gear), p.LAUNCH_RPM)
    return engine.torque_Nm(n) * ratio * p.ETA_DRIVELINE / p.R_TYRE


def traction_limited_speed_ms(mass: Optional[float] = None) -> float:
    """Speed at which drive force equals the *static* traction limit."""
    return p.ETA_DRIVELINE * p.P_RATED_W / traction_limit_N(0.0, mass)


def traction_limited_speed_dynamic_ms(mass: Optional[float] = None) -> float:
    """Speed at which drive force equals the limit *with* load transfer."""
    return p.ETA_DRIVELINE * p.P_RATED_W / traction_limit_dynamic_N(mass)


def top_speed_ms(cd: Optional[float] = None, mass: Optional[float] = None) -> float:
    """Drag-limited top speed: root of eq. (4)."""
    c = p.CD if cd is None else cd
    m = _m(mass)
    avail = p.ETA_DRIVELINE * p.P_RATED_W
    lo, hi = 1.0, 250.0
    while hi - lo > 1e-6:
        mid = 0.5 * (lo + hi)
        need = 0.5 * p.RHO_AIR * c * p.FRONTAL_AREA * mid ** 3 + p.C_RR * m * G * mid
        lo, hi = (lo, mid) if need > avail else (mid, hi)
    return lo


def kinetic_energy_MJ(v_kmh: float, mass: Optional[float] = None) -> float:
    v = v_kmh / 3.6
    return 0.5 * _m(mass) * v * v / 1e6


def simulate_acceleration(mass: Optional[float] = None, v_end_kmh: float = 360.0,
                          dt: Optional[float] = None,
                          mu: Optional[float] = None) -> List[Tuple[float, float, float, int]]:
    """Quasi-steady acceleration run with traction limit and gear shifts.

    Returns (time s, speed m/s, distance m, gear index); gear -1 marks a shift.
    """
    m = _m(mass)
    dt = p.DT if dt is None else dt
    f = p.MU if mu is None else mu
    v = t = x = 0.0
    gear, shift, ax = 0, 0.0, 0.0
    rows = []
    while v < v_end_kmh / 3.6 and t < 120.0:
        if shift <= 0.0 and engine_speed_rpm(v, gear) >= p.SHIFT_RPM \
                and gear + 1 < len(p.GEAR_RATIOS):
            gear += 1
            shift = p.SHIFT_TIME
        if shift > 0.0:
            shift -= dt
            drive = 0.0
            rows.append((t, v, x, -1))
        else:
            drive = min(tractive_force_N(v, gear), traction_limit_N(ax, m, mu=f))
            rows.append((t, v, x, gear))
        ax = (drive - road_load_N(v, m)) / (p.ROT_MASS_FACTOR * m)
        v += ax * dt
        x += v * dt
        t += dt
    return rows


def time_to_speed(rows, v_kmh: float):
    target = v_kmh / 3.6
    for t, v, x, g in rows:
        if v >= target:
            return t
    return float("nan")


def quarter_mile(rows):
    for t, v, x, g in rows:
        if x >= 400.0:
            return t, v * 3.6
    return float("nan"), float("nan")
