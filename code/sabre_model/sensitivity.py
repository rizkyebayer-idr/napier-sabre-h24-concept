# -*- coding: utf-8 -*-
"""
One-at-a-time sensitivity and uncertainty analysis.

Each key input is perturbed over a stated plausible range and the effect on the
headline outputs is reported, so that the uncertainty is quantified rather than
asserted.
"""
from __future__ import annotations

import copy
import math
from typing import Dict, List, Tuple

from . import dynamics, engine, fuel, mass, noise
from . import params as p

# (label, attribute, low multiplier, high multiplier, low value, high value, unit)
PERTURBATIONS = [
    ("Vehicle mass m", "MASS_KG", 0.90, 1.10, None, None, "kg"),
    ("Tyre friction mu", "MU", 0.90, 1.10, None, None, "-"),
    ("FMEP coefficient b", "FMEP_B", 0.80, 1.20, None, None, "bar"),
    ("Indicated efficiency eta_i", "ETA_IND", 0.90, 1.10, None, None, "-"),
    ("Acoustic efficiency eta_ac", "ETA_ACOUSTIC", 0.50, 1.50, None, None, "-"),
    ("Drag coefficient C_D", "CD", 0.90, 1.10, None, None, "-"),
]


def _snapshot():
    return {k: copy.deepcopy(getattr(p, k)) for k in
            ("MASS_KG", "MU", "FMEP_B", "ETA_IND", "ETA_ACOUSTIC", "CD",
             "GEAR_RATIOS", "CG_X", "CG_Z")}


def _restore(snap):
    for k, v in snap.items():
        setattr(p, k, v)


def _refresh_mass_dependent():
    """Keep the mass budget, CG and traction limits consistent with MASS_KG."""
    # scale every mass item so that the total equals MASS_KG
    items = p.MASS_ITEMS
    total = sum(m for _, m, _, _ in items)
    scale = p.MASS_KG / total
    p.MASS_ITEMS = [(lbl, m * scale, x, z) for lbl, m, x, z in items]
    st = mass.compute()
    p.CG_X, p.CG_Z = st.cg_x_m, st.cg_z_m


def _outputs() -> Dict[str, float]:
    st = mass.compute()
    rows = dynamics.simulate_acceleration(v_end_kmh=320.0)
    return {
        "mass": st.total_kg,
        "cg_x": st.cg_x_m,
        "traction_limit_kN": dynamics.traction_limit_N(0.0) / 1e3,
        "v_traction_kmh": dynamics.traction_limited_speed_ms() * 3.6,
        "0_100_s": dynamics.time_to_speed(rows, 100),
        "0_200_s": dynamics.time_to_speed(rows, 200),
        "vmax_kmh": dynamics.top_speed_ms() * 3.6,
        "fuel_100": fuel.consumption_at_speed(100)[0],
        "fuel_300": fuel.consumption_at_speed(300)[0],
        "idle_Lh": fuel.idle_litres_per_hour(),
        "Lp_dB": noise.unsilenced_levels()[1][1],
    }


def run() -> List[dict]:
    """One-at-a-time study; returns a row per perturbation."""
    base_snap = _snapshot()
    base = _outputs()

    results = []
    for label, attr, lo_mul, hi_mul, *_ in PERTURBATIONS:
        row = {"label": label, "attr": attr, "base": base, "cases": []}
        for mul in (lo_mul, hi_mul):
            _restore(base_snap)
            if attr == "MASS_KG":
                p.MASS_KG = base_snap["MASS_KG"] * mul
                _refresh_mass_dependent()
            elif attr == "ETA_ACOUSTIC":
                p.ETA_ACOUSTIC = tuple(x * mul for x in base_snap["ETA_ACOUSTIC"])
            else:
                setattr(p, attr, base_snap[attr] * mul)
            row["cases"].append((mul, _outputs()))
        results.append(row)
    _restore(base_snap)
    return results


def summarise(results, key: str) -> Tuple[float, float, float]:
    """(low, base, high) of an output across every perturbation case."""
    base = results[0]["base"][key]
    vals = [c[1][key] for r in results for c in r["cases"]]
    return min(vals), base, max(vals)


def table():
    """Rows ready for a results table."""
    res = run()
    keys = [("0_100_s", "0-100 km/h [s]", 1),
            ("vmax_kmh", "Theoretical v_max [km/h]", 0),
            ("fuel_100", "Fuel at 100 km/h [L/100 km]", 0),
            ("fuel_300", "Fuel at 300 km/h [L/100 km]", 0),
            ("Lp_dB", "Unsilenced L_p at 7.5 m [dB]", 0)]
    out = []
    for r in res:
        low = r["cases"][0][1]
        high = r["cases"][1][1]
        line = [r["label"]]
        for k, _lbl, nd in keys:
            line.append(f"{low[k]:.{nd}f} / {high[k]:.{nd}f}")
        out.append(line)
    header = ["Parameter"] + [lbl for _k, lbl, _nd in keys]
    base = ["Nominal"] + [f"{res[0]['base'][k]:.{nd}f}" for k, _l, nd in keys]
    return header, base, out


if __name__ == "__main__":
    h, b, rows = table()
    print("\t".join(h))
    print("\t".join(b))
    for r in rows:
        print("\t".join(r))
