# -*- coding: utf-8 -*-
"""Mass properties and static stability, eq. (6)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from . import params as p

G = 9.81


@dataclass
class MassState:
    total_kg: float
    cg_x_m: float
    cg_z_m: float
    front_fraction: float
    rear_fraction: float
    ssf: float


def compute(items=None) -> MassState:
    items = items or p.MASS_ITEMS
    total = sum(m for _, m, _, _ in items)
    xcg = sum(m * x for _, m, x, _ in items) / total
    zcg = sum(m * z for _, m, _, z in items) / total
    front = (p.WHEELBASE - xcg) / p.WHEELBASE
    return MassState(total, xcg, zcg, front, 1.0 - front, p.TRACK / (2.0 * zcg))


def braking_transfer_kg(state: MassState, decel_g: float = 1.0) -> float:
    """Load moved onto the front axle under braking [kg]."""
    return state.total_kg * G * decel_g * state.cg_z_m / p.WHEELBASE / G


def cornering_transfer_kg(state: MassState, lat_g: float = 1.0) -> float:
    """Load moved onto the outer wheels in a constant-radius turn [kg]."""
    return state.total_kg * G * lat_g * state.cg_z_m / p.TRACK / G


def table(items=None) -> List[str]:
    items = items or p.MASS_ITEMS
    st = compute(items)
    out = [f"{'Component':52s}{'m (kg)':>10s}{'x (m)':>9s}{'z (m)':>9s}"]
    for label, m, x, z in items:
        out.append(f"{label:52s}{m:10.0f}{x:9.2f}{z:9.2f}")
    out.append(f"{'TOTAL / CG':52s}{st.total_kg:10.0f}{st.cg_x_m:9.2f}{st.cg_z_m:9.2f}")
    return out
