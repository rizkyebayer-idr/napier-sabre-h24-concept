# -*- coding: utf-8 -*-
"""
Model validation.

The same models are applied unchanged to a production car with published
performance, so that the error of the approach can be measured rather than
assumed.

The Bugatti Chiron is used because its tyres, brakes and wheelbase already serve
as dimensional references in the packaging study, and its rated power is almost
identical to the de-rated Sabre.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

from . import dynamics, engine, fuel, noise
from . import params as p

G = 9.81


# ---------------------------------------------------------------------------
# A generic vehicle description that both the Sabre concept and the Chiron fit
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    name: str
    mass: float                 # kg, incl. driver
    power_W: float              # rated brake power
    n_rated: float              # rpm at rated power
    torque_limit: float         # N.m (set very high for a road car map)
    cd: float
    area: float
    r_tyre: float
    ratios: Tuple[float, ...]
    drive: str = "RWD"          # 'RWD' or 'AWD'
    cg_x: float = 2.0           # m behind front axle
    cg_z: float = 0.45
    wheelbase: float = 2.7
    mu: float = 1.15
    crr: float = 0.011
    eta_d: float = 0.90
    rot_factor: float = 1.06


def _power(vh: Vehicle, n_rpm: float) -> float:
    """Cubic map capped at the rated power, evaluated for any vehicle."""
    if n_rpm <= 0:
        return 0.0
    x = min(n_rpm / vh.n_rated, 1.0)
    return vh.power_W * (x + x * x - x ** 3)


def _torque(vh: Vehicle, n_rpm: float) -> float:
    if n_rpm <= 0:
        return 0.0
    w = n_rpm * 2 * math.pi / 60
    return min(_power(vh, n_rpm) / w, vh.torque_limit)


def _engine_rpm(vh: Vehicle, v: float, gear: int) -> float:
    return v / vh.r_tyre * vh.ratios[gear] * 60 / (2 * math.pi)


def _road_load(vh: Vehicle, v: float) -> float:
    return 0.5 * p.RHO_AIR * vh.cd * vh.area * v * v + vh.crr * vh.mass * G


def _drive_force(vh: Vehicle, v: float, gear: int) -> float:
    n = _engine_rpm(vh, v, gear)
    n = max(n, 1500.0)                       # clutch slip at launch
    return _torque(vh, n) * vh.ratios[gear] * vh.eta_d / vh.r_tyre


def _traction_limit(vh: Vehicle, ax: float) -> float:
    static = vh.mass * G * vh.cg_x / vh.wheelbase
    transfer = vh.mass * ax * vh.cg_z / vh.wheelbase
    if vh.drive == "AWD":
        return vh.mu * vh.mass * G
    return vh.mu * (static + transfer)


def simulate(vh: Vehicle, v_end_kmh: float = 320.0, dt: float = 0.01):
    """Quasi-steady acceleration run, same structure as dynamics.simulate_*."""
    v = t = x = 0.0
    gear, shift = 0, 0.0
    ax = 0.0
    out = []
    while v < v_end_kmh / 3.6 and t < 120:
        if shift <= 0 and _engine_rpm(vh, v, gear) >= vh.n_rated and gear + 1 < len(vh.ratios):
            gear += 1
            shift = 0.25
        if shift > 0:
            shift -= dt
            drive = 0.0
        else:
            drive = min(_drive_force(vh, v, gear), _traction_limit(vh, ax))
        out.append((t, v, x))
        ax = (drive - _road_load(vh, v)) / (vh.rot_factor * vh.mass)
        v += ax * dt
        x += v * dt
        t += dt
    return out


def time_to(rows, kmh: float) -> float:
    target = kmh / 3.6
    for t, v, x in rows:
        if v >= target:
            return t
    return float("nan")


def vmax(vh: Vehicle) -> float:
    avail = vh.eta_d * vh.power_W
    lo, hi = 1.0, 250.0
    while hi - lo > 1e-6:
        mid = 0.5 * (lo + hi)
        need = 0.5 * p.RHO_AIR * vh.cd * vh.area * mid ** 3 + vh.crr * vh.mass * G * mid
        lo, hi = (lo, mid) if need > avail else (mid, hi)
    return lo


# ---------------------------------------------------------------------------
# Chiron: published data, then the same models applied to it
# ---------------------------------------------------------------------------
CHIRON = Vehicle(
    name="Bugatti Chiron",
    mass=1995.0,                 # R  DIN kerb mass
    power_W=1103e3,              # R  1500 PS
    n_rated=6700.0,              # R
    torque_limit=1600.0,         # R  N.m, 2000-6000 rpm
    cd=0.38,                     # R  (manufacturer figure, top-speed mode 0.35)
    area=2.07,                   # E  estimated from 2038 mm width and 1212 mm height
    r_tyre=0.353,                # R  355/25 R21
    ratios=(11.43, 8.10, 6.02, 4.57, 3.64, 2.88, 2.34),  # E 7 speeds, 6,700 rpm
    drive="AWD",
    cg_x=1.35, cg_z=0.42, wheelbase=2.711,
    mu=1.15, crr=0.011, eta_d=0.90,
)

CHIRON_PUBLISHED = {
    "0-100": 2.4,      # s
    "0-200": 6.5,      # s
    "0-300": 13.1,     # s
    "vmax": 420.0,     # km/h, electronically limited
}


def chiron_study(mu: float = None) -> Dict[str, object]:
    vh = CHIRON
    if mu is not None:
        import copy as _copy
        vh = _copy.deepcopy(CHIRON)
        vh.mu = mu
    rows = simulate(vh, v_end_kmh=340.0)
    model = {
        "0-100": time_to(rows, 100),
        "0-200": time_to(rows, 200),
        "0-300": time_to(rows, 300),
        "vmax": vmax(vh) * 3.6,
    }
    err = {k: 100.0 * (model[k] - CHIRON_PUBLISHED[k]) / CHIRON_PUBLISHED[k]
           for k in model}
    return {"model": model, "published": CHIRON_PUBLISHED, "error_pct": err}


def sabre_study() -> Dict[str, float]:
    """The same generic model applied to the Sabre concept, for cross-checking."""
    sabre = Vehicle(
        name="Sabre concept",
        mass=p.MASS_KG, power_W=p.P_RATED_W, n_rated=p.N_RATED,
        torque_limit=p.T_LIMIT, cd=p.CD, area=p.FRONTAL_AREA,
        r_tyre=p.R_TYRE, ratios=p.GEAR_RATIOS, drive="RWD",
        cg_x=p.CG_X, cg_z=p.CG_Z, wheelbase=p.WHEELBASE,
        mu=p.MU, crr=p.C_RR, eta_d=p.ETA_DRIVELINE,
    )
    rows = simulate(sabre, v_end_kmh=320.0)
    return {"0-100": time_to(rows, 100), "0-200": time_to(rows, 200),
            "0-300": time_to(rows, 300), "vmax": vmax(sabre) * 3.6}
