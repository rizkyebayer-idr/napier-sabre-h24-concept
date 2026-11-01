# -*- coding: utf-8 -*-
"""
Tyre load check.

The static rear-axle load at the governed speed is close to the load index of the
adopted tyre, and load capacity must be derated above 240 km/h, so this is a
first-order constraint on the concept.
"""
from __future__ import annotations

from . import mass
from . import params as p


def static_axle_loads_kg():
    st = mass.compute()
    front = st.total_kg * st.front_fraction
    rear = st.total_kg * st.rear_fraction
    return front, rear


def per_tyre_load_kg(axle: str = "rear", lateral_g: float = 0.0):
    """Static load per tyre, plus the extra load from a lateral manoeuvre."""
    front, rear = static_axle_loads_kg()
    base = (front if axle == "front" else rear) / 2.0
    transfer = mass.cornering_transfer_kg(mass.compute(), lateral_g) / 2.0
    return base, base + transfer


def capacity_at_speed_kg(derate=None):
    """Permissible load per tyre once speed derating is applied."""
    derate = p.TYRE_SPEED_DERATE if derate is None else derate
    return tuple(p.TYRE_STATIC_LOAD_LIMIT * d for d in derate)


def check():
    base, corner = per_tyre_load_kg("rear", 0.0)
    cap = capacity_at_speed_kg()
    return {
        "rear_axle_kg": static_axle_loads_kg()[1],
        "per_tyre_kg": base,
        "capacity_kg": cap,
        "margin_kg": tuple(c - base for c in cap),
        "adequate": all(c >= base for c in cap),
    }
