# -*- coding: utf-8 -*-
"""
Verify the model against its reference values.

    python code/run_all.py

Every check prints the model value, the reference value and the deviation; the
script exits non-zero if any check fails, so it doubles as a regression test.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sabre_model import (dynamics, engine, fuel, mass, noise, thermal, tyre,
                         validation)
from sabre_model import params as p

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)

CHECKS = []


def check(label, model, ref, unit="", tol=0.06):
    ok = abs(float(model) - float(ref)) <= tol * max(abs(float(ref)), 1e-9)
    CHECKS.append((label, model, ref, unit, ok))
    flag = "ok  " if ok else "DIFF"
    print(f"  [{flag}] {label:42s} model {model:>10.2f} {unit:<9s} "
          f"ref {ref:>9.2f}")
    return ok


def head(t):
    print(f"\n{t}\n" + "-" * len(t))


# ---------------------------------------------------------------- 1. engine
head("1. ENGINE")
print(f"  torque limit binds below          {engine.torque_limited_speed():.0f} rpm "
      f"(ref 3,150)")
print(f"  BSFC implied by the fuel model    "
      f"{engine.fuel_flow_kgs(p.N_RATED, p.P_RATED_W) * 3600 / (p.P_RATED_W / 1e3):.0f} g/kWh "
      f"(ref 418)")

# ---------------------------------------------------------------- 2. mass
head("2. MASS PROPERTIES")
st = mass.compute()
for row in mass.table():
    print("  " + row)
check("total mass", st.total_kg, 3225, "kg")
check("CG position x", st.cg_x_m, 2.38, "m")
check("CG height z", st.cg_z_m, 0.54, "m")
check("front weight fraction", 100 * st.front_fraction, 41, "%", tol=0.05)
check("static stability factor", st.ssf, 1.59, "-")
check("braking transfer at 1 g", mass.braking_transfer_kg(st), 440, "kg", tol=0.05)
check("cornering transfer at 1 g", mass.cornering_transfer_kg(st), 1020, "kg", tol=0.06)
check("power-to-mass", p.P_RATED_W / 1e3 / (st.total_kg / 1000), 341, "kW/t", tol=0.01)

# ---------------------------------------------------------------- 3. traction
head("3. TRACTION")
static = dynamics.traction_limit_N(0.0)
dyn = dynamics.traction_limit_dynamic_N()
print(f"  static limit {static/1e3:.2f} kN -> {dynamics.traction_limited_speed_ms()*3.6:.0f} km/h")
print(f"  with transfer {dyn/1e3:.2f} kN -> {dynamics.traction_limited_speed_dynamic_ms()*3.6:.0f} km/h")
check("static traction limit", static / 1e3, 21.6, "kN", tol=0.02)
check("dynamic traction limit", dyn / 1e3, 25.3, "kN", tol=0.02)
check("traction-limited up to", dynamics.traction_limited_speed_dynamic_ms() * 3.6, 138, "km/h", tol=0.03)

# ---------------------------------------------------------------- 4. performance
head("4. PERFORMANCE")
print("  gear tops: " + ", ".join(f"{v:.0f}" for v in dynamics.gear_top_speeds_kmh()) + " km/h")
check("top gear top speed", dynamics.gear_top_speeds_kmh()[4], 350, "km/h", tol=0.01)
check("theoretical v_max", dynamics.top_speed_ms() * 3.6, 428, "km/h", tol=0.02)
for cd, ref in ((0.30, 463), (0.46, 403)):
    check(f"v_max at CD={cd:.2f}", dynamics.top_speed_ms(cd) * 3.6, ref, "km/h", tol=0.02)

rows = dynamics.simulate_acceleration(v_end_kmh=320)
t400, v400 = dynamics.quarter_mile(rows)
check("0-100 km/h", dynamics.time_to_speed(rows, 100), 4.1, "s", tol=0.05)
check("0-200 km/h", dynamics.time_to_speed(rows, 200), 9.8, "s", tol=0.05)
check("0-300 km/h", dynamics.time_to_speed(rows, 300), 20.8, "s", tol=0.05)
check("400 m time", t400, 11.4, "s", tol=0.05)
check("400 m speed", v400, 220, "km/h", tol=0.05)
check("kinetic energy at 100", dynamics.kinetic_energy_MJ(100), 1.24, "MJ", tol=0.02)
check("kinetic energy at 350", dynamics.kinetic_energy_MJ(350), 15.2, "MJ", tol=0.02)

# ---------------------------------------------------------------- 5. fuel
head("5. FUEL CONSUMPTION")
check("idle", fuel.idle_litres_per_hour(), 16, "L/h", tol=0.10)
for v, ref in ((60, 48), (100, 31), (150, 41), (200, 55), (250, 73), (300, 94)):
    lp, n, g = fuel.consumption_at_speed(v)
    check(f"{v} km/h", lp, ref, "L/100km", tol=0.06)
    print(f"        {n:.0f} rpm, gear {g+1}")
check("full power", fuel.full_power_litres_per_hour(), 530, "L/h", tol=0.05)

# ---------------------------------------------------------------- 6. cooling
head("6. COOLING")
for r in thermal.face_velocity_sensitivity():
    print(f"  {r['heat_kW']:5.0f} kW -> {r['mdot_kgs']:5.1f} kg/s | core area "
          f"{r['area_25_ms']:.2f} m2 @25 m/s, {r['area_hi_ms']:.2f} @12, "
          f"{r['area_lo_ms']:.2f} @8")
print(f"  packaged core area {thermal.packaged_core_area_m2():.2f} m2")
fp = thermal.fan_power_W(thermal.cooling_air_flow_kgs(880e3))
print(f"  fan power at 880 kW: {fp[0]/1e3:.1f}-{fp[1]/1e3:.1f} kW")
burst = {v: thermal.coolant_burst_seconds(v) for v in (100, 200, 350)}
print("  full-power burst: " + ", ".join(f"{v} km/h -> {t:.1f} s" for v, t in burst.items()))
check("cooling air flow (upper)", thermal.cooling_air_flow_kgs(880e3), 29, "kg/s", tol=0.06)
check("burst at 100 km/h", burst[100], 4.5, "s", tol=0.20)

# ---------------------------------------------------------------- 7. tyre
head("7. TYRE LOAD")
ty = tyre.check()
print(f"  rear axle {ty['rear_axle_kg']:.0f} kg -> {ty['per_tyre_kg']:.0f} kg per tyre")
print(f"  capacity at 350 km/h {ty['capacity_kg'][0]:.0f}-{ty['capacity_kg'][1]:.0f} kg "
      f"-> adequate: {ty['adequate']}")
check("rear axle load", ty["rear_axle_kg"], 1915, "kg", tol=0.01)
check("load per tyre", ty["per_tyre_kg"], 958, "kg", tol=0.01)

# ---------------------------------------------------------------- 8. noise
head("8. EXHAUST NOISE")
levels, f, corr = noise.unsilenced_levels_dbA()
print(f"  firing frequency {f:.0f} Hz, A-weighting {corr:+.1f} dB")
for lw, lp in levels:
    print(f"    LW {lw:6.1f} dB -> Lp(A) {lp:6.1f} dB(A) at {p.R_PASSBY} m")
rows_n, lo, hi = noise.noise_budget()
for a, b in rows_n:
    print(f"    {a:48s} {b}")
att = noise.required_attenuation_dB()
print(f"  attenuation needed vs {p.PASSBY_LIMIT_DBA:.0f} dB(A): {att[0]:.1f}-{att[1]:.1f} dB")
check("Lp(A) lower", levels[0][1], 98, "dB(A)", tol=0.02)
check("Lp(A) upper", levels[1][1], 108, "dB(A)", tol=0.02)
check("worst-case silenced level", hi, 80, "dB(A)", tol=0.03)

# ---------------------------------------------------------------- 9. validation
head("9. VALIDATION AGAINST A PRODUCTION CAR")
ch = validation.chiron_study()
ch2 = validation.chiron_study(mu=1.35)
for k, ref in (("0-100", 2.40), ("0-200", 6.50), ("0-300", 13.10), ("vmax", 420.0)):
    check(f"reference car {k}", ch["model"][k], ref, "s" if k != "vmax" else "km/h", tol=0.25)
check("reference car 0-100 with mu=1.35", ch2["model"]["0-100"], 2.40, "s", tol=0.06)

# ---------------------------------------------------------------- summary
head("SUMMARY")
n_ok = sum(1 for c in CHECKS if c[4])
print(f"  {n_ok}/{len(CHECKS)} checks pass")
for label, model, ref, unit, ok in CHECKS:
    if not ok:
        print(f"    DIFF {label}: {model:.2f} vs {ref} {unit}")

with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as fh:
    json.dump({"checks": [{"label": a, "model": b, "ref": c, "unit": d, "ok": e}
                          for a, b, c, d, e in CHECKS],
               "mass": st.__dict__}, fh, indent=1, ensure_ascii=False)
print(f"\nwritten to {os.path.join(OUT, 'results.json')}")
sys.exit(0 if n_ok == len(CHECKS) else 1)
