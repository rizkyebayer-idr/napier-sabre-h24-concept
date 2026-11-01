# -*- coding: utf-8 -*-
"""
Exhaust noise, the silencing budget and A-weighting.

The legal pass-by limit is A-weighted, so the estimate is evaluated at the firing
frequency and corrected with the standard A-weighting curve rather than compared
as an unweighted level. The full-power condition is an upper bound: the UN R51
pass-by test is a part-load acceleration test.
"""
from __future__ import annotations

import math

from . import params as p


def a_weighting_db(f_hz: float) -> float:
    """A-weighting correction [dB] at frequency f (IEC 61672-1)."""
    if f_hz <= 0:
        return -math.inf
    f2 = f_hz * f_hz
    num = (12194.0 ** 2) * f2 * f2
    den = ((f2 + 20.6 ** 2)
           * math.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2))
           * (f2 + 12194.0 ** 2))
    return 20.0 * math.log10(num / den) + 2.00


def sound_power_level_dB(eta_ac: float, power_W: float = p.P_RATED_W) -> float:
    """Sound power level from acoustic conversion efficiency."""
    return 10.0 * math.log10(eta_ac * power_W / p.W_REF)


def sound_pressure_level_dB(lw_dB: float, r: float = p.R_PASSBY) -> float:
    """SPL at distance r over a reflecting ground plane."""
    return lw_dB - 20.0 * math.log10(r) - 8.0


def firing_frequency_Hz(n_rpm: float) -> float:
    """Fundamental exhaust firing frequency for 24 cylinders: 24 n / 120."""
    return 24.0 * n_rpm / 120.0


def unsilenced_levels():
    """(LW bracket, unweighted Lp bracket) at rated power."""
    out = []
    for eta in p.ETA_ACOUSTIC:
        lw = sound_power_level_dB(eta)
        out.append((lw, sound_pressure_level_dB(lw)))
    return out


def unsilenced_levels_dbA(n_rpm: float = p.N_RATED):
    """(levels in dB(A), firing frequency, weighting correction)."""
    f = firing_frequency_Hz(n_rpm)
    corr = a_weighting_db(f)
    return tuple((lw, lp + corr) for lw, lp in unsilenced_levels()), f, corr


def _lps(n_rpm=p.N_RATED, weighted=True):
    if not weighted:
        return [lp for _, lp in unsilenced_levels()]
    return [lp for _, lp in unsilenced_levels_dbA(n_rpm)[0]]


def required_attenuation_dB(limit=None, weighted=True, n_rpm=p.N_RATED):
    """Attenuation needed to reach the pass-by limit.

    Returns (minimum, maximum) over the acoustic-efficiency bracket.
    """
    limit = p.PASSBY_LIMIT_DBA if limit is None else limit
    need = [lp - limit for lp in _lps(n_rpm, weighted)]
    return min(need), max(need)


STAGES = (("Four-branch manifolds + resonators", (10, 15)),
          ("Absorptive main silencers", (15, 20)),
          ("Engine-bay acoustic enclosure", (3, 5)))


def noise_budget(stages=STAGES, weighted=True, n_rpm=p.N_RATED):
    """Walk through the silencing chain.

    Returns (rows, final_low, final_high). The range is the cross-combination of
    the acoustic-efficiency bracket and the attenuation bracket, i.e. the best
    and the worst case.
    """
    lps = _lps(n_rpm, weighted)
    lo_src, hi_src = min(lps), max(lps)
    total_min = sum(a for _, (a, _b) in stages)
    total_max = sum(b for _, (_a, b) in stages)

    rows = [("Unsilenced exhaust at rated power (estimated)",
             f"{lo_src:.0f}-{hi_src:.0f}")]
    for name, (a, b) in stages:
        rows.append((name, f"-{a} to -{b}"))
    rows.append(("Resulting exhaust level (best / worst case)",
                 f"{lo_src - total_max:.0f} / {hi_src - total_min:.0f}"))
    rows.append(("EU phase-3 pass-by limit, PMR > 200 kW/t",
                 f"{p.PASSBY_LIMIT_DBA:.0f}"))
    return rows, lo_src - total_max, hi_src - total_min
