# -*- coding: utf-8 -*-
"""Print the validation, sensitivity, cooling, tyre and noise analyses."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sabre_model import (dynamics, mass, noise, sensitivity, thermal, tyre,
                         validation)
from sabre_model import params as p

print("=== 1. VALIDATION (Chiron) ===")
ch = validation.chiron_study()
for k in ch["model"]:
    print(f"  {k:6s} model {ch['model'][k]:8.2f}  published {ch['published'][k]:8.2f}  "
          f"error {ch['error_pct'][k]:+6.1f} %")
print("  Sabre via same generic model:", {k: round(v, 2) for k, v in validation.sabre_study().items()})

print("\n=== 2. TRACTION LIMIT (static vs with load transfer) ===")
st = mass.compute()
print(f"  static            {dynamics.traction_limit_N(0.0)/1e3:.2f} kN")
dyn = dynamics.traction_limit_dynamic_N()
print(f"  with transfer     {dyn/1e3:.2f} kN")
print(f"  traction-limited up to (static) {dynamics.traction_limit_N(0)/1e3:6.2f} kN -> "
      f"{p.ETA_DRIVELINE*p.P_RATED_W/dynamics.traction_limit_N(0)*3.6:.0f} km/h")
print(f"  traction-limited up to (dynamic)                        -> "
      f"{p.ETA_DRIVELINE*p.P_RATED_W/dyn*3.6:.0f} km/h")

print("\n=== 3. COOLING at realistic face velocity ===")
for r in thermal.face_velocity_sensitivity():
    print(f"  {r['heat_kW']:5.0f} kW -> {r['mdot_kgs']:5.1f} kg/s air | "
          f"A@25 m/s {r['area_25_ms']:4.2f} | A@12 {r['area_hi_ms']:4.2f} | "
          f"A@8 {r['area_lo_ms']:4.2f} m2")
print(f"  packaged core area: {thermal.packaged_core_area_m2():.2f} m2")
fp = thermal.fan_power_W(thermal.cooling_air_flow_kgs(880e3))
print(f"  fan/ram power at 880 kW: {fp[0]/1e3:.1f}-{fp[1]/1e3:.1f} kW")
print("  burst duration (ambient 30 C): ", end="")
for v in (100, 200, 300, 350):
    t = thermal.coolant_burst_seconds(v)
    print(f"{v} km/h -> {t if t==float('inf') else round(t,1)} s", end="; ")
print()

print("\n=== 4. TYRE LOAD ===")
c = tyre.check()
print("  ", c)

print("\n=== 5. NOISE, A-weighted ===")
lv, f, corr = noise.unsilenced_levels_dbA()
print(f"  firing frequency {f:.0f} Hz, A-weighting {corr:+.1f} dB")
for lw, lp in lv:
    print(f"   LW {lw:6.1f} dB -> Lp(A) {lp:6.1f} dB(A) at 7.5 m")
rows, lo, hi = noise.noise_budget()
for n, v in rows:
    print(f"   {n:48s} {v}")
print(f"   -> best {lo:.0f} dB(A), worst {hi:.0f} dB(A); limit 72 dB(A)")
att = noise.required_attenuation_dB()
print(f"  attenuation needed vs 72 dB(A): {att[0]:.1f}-{att[1]:.1f} dB")
lv800, f800, c800 = noise.unsilenced_levels_dbA(800)
print(f"  idle {f800:.0f} Hz, weighting {c800:+.1f} dB -> "
      f"{lv800[0][1]:.0f}-{lv800[1][1]:.0f} dB(A)")

print("\n=== 6. SENSITIVITY ===")
h, b, rows = sensitivity.table()
print("\t" + "\t".join(h))
print("\t" + "\t".join(b))
for r in rows:
    print("\t" + "\t".join(r))
