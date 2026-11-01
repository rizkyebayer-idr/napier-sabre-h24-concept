# -*- coding: utf-8 -*-
"""Engine model: power curve, torque limit and specific fuel consumption."""
from __future__ import annotations

import math

from . import params as p


def power_W(n_rpm: float) -> float:
    """Full-load brake power, cubic approximation, eq. (1).

        P(n) = Pr (x + x^2 - x^3) ,  x = n / nr

    The curve is capped at the rated power for n > nr.
    """
    if n_rpm <= 0.0:
        return 0.0
    x = min(n_rpm / p.N_RATED, 1.0)
    return p.P_RATED_W * (x + x * x - x ** 3)


def torque_Nm(n_rpm: float) -> float:
    """Brake torque, limited electronically to T_LIMIT."""
    if n_rpm <= 0.0:
        return 0.0
    omega = n_rpm * 2.0 * math.pi / 60.0
    return min(power_W(n_rpm) / omega, p.T_LIMIT)


def power_from_torque(n_rpm: float) -> float:
    """Brake power actually available once the torque limit is applied."""
    return torque_Nm(n_rpm) * n_rpm * 2.0 * math.pi / 60.0


def torque_limited_speed() -> float:
    """Highest engine speed [rpm] at which the torque limit still binds.

    The cubic curve delivers more than T_LIMIT only over a mid-speed band.
    Above the speed returned here the gear curves leave the flat 3,300 N.m
    plateau and start to follow the power hyperbola.
    """
    def excess(n: float) -> float:
        w = n * 2.0 * math.pi / 60.0
        return power_W(n) / w - p.T_LIMIT

    n = p.N_RATED
    while n > 100.0:
        if excess(n) > 0.0:
            return n
        n -= 1.0
    return 0.0


def fmep_bar(n_rpm: float) -> float:
    """Friction mean effective pressure, incl. sleeve drive and supercharger."""
    return p.FMEP_A + p.FMEP_B * (n_rpm / 1000.0) ** 2


def pmep_bar(n_rpm: float, brake_power_W: float) -> float:
    """Pumping mean effective pressure: high at light load, zero at full load."""
    load = 0.0 if p.P_RATED_W <= 0 else min(brake_power_W / p.P_RATED_W, 1.0)
    return p.PMEP_LIGHT + (p.PMEP_FULL - p.PMEP_LIGHT) * load


def fuel_flow_kgs(n_rpm: float, brake_power_W: float) -> float:
    """Fuel mass flow, eq. (7).

        mdot_f = phi [ Pb + (FMEP + PMEP) Vd n / 120 ] / (eta_i Q_LHV)

    FMEP and PMEP in Pa, n in rpm, Vd in m3 -> W.
    """
    if n_rpm <= 0.0:
        return 0.0
    loss = (fmep_bar(n_rpm) + pmep_bar(n_rpm, brake_power_W)) * 1e5 \
        * p.DISPLACEMENT * n_rpm / 120.0
    return p.PHI_FUEL * (brake_power_W + loss) / (p.ETA_IND * p.Q_LHV)


def fuel_flow_full_power_kgh() -> float:
    """Full-load fuel flow from brake specific fuel consumption [kg/h]."""
    return p.BSFC_FULL * p.P_RATED_W * 3600.0
