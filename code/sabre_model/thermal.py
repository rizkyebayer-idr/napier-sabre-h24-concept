# -*- coding: utf-8 -*-
"""
Heat rejection, radiator sizing and the coolant thermal-inertia burst.

A core face velocity of 25 m/s is optimistic for vehicle practice, so the sizing
is given both at that value and at realistic vehicle values (8-12 m/s), together
with the resulting pressure drop and fan power. The length of time for which full
power can be held is estimated from the coolant's thermal capacity.
"""
from __future__ import annotations

import math

from . import params as p


def heat_rejected_W(power_W: float = p.P_RATED_W):
    """Heat to coolant and oil at full load [W] (bracket)."""
    return tuple(f * power_W for f in p.HEAT_FRACTION)


def cooling_air_flow_kgs(heat_W):
    """Mass flow of cooling air for a given heat rejection, eq. (9)."""
    return heat_W / (p.CP_AIR * p.DELTA_T_AIR)


def radiator_face_area_m2(mdot_kgs, face_velocity=None):
    """Core face area for a given air mass flow and face velocity."""
    v = p.FACE_VELOCITY if face_velocity is None else face_velocity
    return mdot_kgs / (p.RHO_AIR * v)


def packaged_core_area_m2(n_modules: int = 3, core=(0.705, 0.448)) -> float:
    """Core area actually available with the radiator modules of Fig. 1."""
    return n_modules * core[0] * core[1]


def face_velocity_sensitivity():
    """Required core area at the optimistic and the realistic face velocities."""
    rows = []
    for h in heat_rejected_W():
        mdot = cooling_air_flow_kgs(h)
        rows.append({
            "heat_kW": h / 1e3,
            "mdot_kgs": mdot,
            "area_25_ms": radiator_face_area_m2(mdot, p.FACE_VELOCITY),
            "area_lo_ms": radiator_face_area_m2(mdot, p.FACE_VELOCITY_RANGE[0]),
            "area_hi_ms": radiator_face_area_m2(mdot, p.FACE_VELOCITY_RANGE[1]),
        })
    return rows


def fan_power_W(mdot_kgs, velocity=None):
    """Air-side pumping power for the radiator cores.

    Uses an assumed core pressure drop (250-400 Pa at realistic face velocities,
    i.e. a loss coefficient of 4-7 referred to the face dynamic head) and a fan
    total efficiency of 0.55.
    """
    v = p.FACE_VELOCITY_RANGE[1] if velocity is None else velocity
    out = []
    for dp in p.CORE_PRESSURE_DROP:
        vol_flow = mdot_kgs / p.RHO_AIR
        out.append(dp * vol_flow / p.FAN_EFFICIENCY)
    return tuple(out)


def coolant_burst_seconds(v_kmh: float, ambient_C: float = p.AMBIENT_C):
    """How long full power can be held before the coolant reaches its limit.

    Simple lumped thermal capacity: the engine dumps Q_rej into the circuit, the
    radiator removes what the airflow allows at that road speed, and the coolant
    (mass m_c, specific heat cp) absorbs the difference until it reaches
    COOLANT_LIMIT_C from its steady 90 C operating point.
    """
    heat = p.HEAT_FRACTION[1] * p.P_RATED_W          # worst case, 880 kW
    # radiator capacity scales with the square root of face velocity (ram air)
    v_ref = p.V_GOVERNED
    v = max(v_kmh / 3.6, 1.0)
    capacity = heat * min(1.0, (v / v_ref) ** 0.5)
    # at high ambient the available dT shrinks
    capacity *= max(0.0, (p.COOLANT_LIMIT_C - ambient_C) / (p.COOLANT_LIMIT_C - 20.0))
    surplus = heat - capacity
    if surplus <= 0:
        return math.inf
    energy = p.COOLANT_MASS * p.COOLANT_CP * (p.COOLANT_LIMIT_C - 90.0)
    return energy / surplus


def summary():
    return face_velocity_sensitivity()
