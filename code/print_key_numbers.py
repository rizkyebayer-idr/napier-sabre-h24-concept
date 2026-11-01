import os
import sys

sys.path.insert(0, r"D:\Riset\Napier_Sabre\code")

from sabre_model import (dynamics, engine, fuel, mass, noise, thermal, tyre,
                         validation)
from sabre_model import params as p

print("GEAR TOPS:", [round(v) for v in dynamics.gear_top_speeds_kmh()])
print("TQ LIMIT BINDS UP TO:", round(engine.torque_limited_speed()), "rpm")
print("TRACTION static/dyn kN:", round(dynamics.traction_limit_N(0) / 1e3, 2),
      round(dynamics.traction_limit_dynamic_N() / 1e3, 2))
print("TRACTION speeds km/h:", round(dynamics.traction_limited_speed_ms() * 3.6),
      round(dynamics.traction_limited_speed_dynamic_ms() * 3.6))
print("VMAX:", round(dynamics.top_speed_ms() * 3.6, 1),
      "at CD .30/.46:", round(dynamics.top_speed_ms(0.30) * 3.6),
      round(dynamics.top_speed_ms(0.46) * 3.6))

rows = dynamics.simulate_acceleration(v_end_kmh=320)
print("ACCEL:", round(dynamics.time_to_speed(rows, 100), 2),
      round(dynamics.time_to_speed(rows, 200), 2),
      round(dynamics.time_to_speed(rows, 300), 2),
      "400m", [round(x, 2) if isinstance(x, float) else x
               for x in dynamics.quarter_mile(rows)])

print("FUEL TABLE:")
for v in (60, 100, 150, 200, 250, 300):
    lp, n, g = fuel.consumption_at_speed(v)
    print(f"   {v:3d} km/h  {lp:5.1f} L/100km  {n:5.0f} rpm  gear {g+1}")
print("   idle", round(fuel.idle_litres_per_hour(), 1), "L/h")
print("   full", round(fuel.full_power_litres_per_hour(), 1), "L/h")
print("   BSFC implied by eq(7) at rated:",
      round(engine.fuel_flow_kgs(p.N_RATED, p.P_RATED_W) * 3600 / (p.P_RATED_W / 1000), 1),
      "g/kWh")

st = mass.compute()
print("MASS:", round(st.total_kg), round(st.cg_x_m, 2), round(st.cg_z_m, 2),
      f"F{st.front_fraction*100:.0f}:R{st.rear_fraction*100:.0f}", round(st.ssf, 2))
print("TRANSFER brake/corner kg:", round(mass.braking_transfer_kg(st)),
      round(mass.cornering_transfer_kg(st)))
print("POWER/MASS:", round(p.P_RATED_W / 1e3 / (st.total_kg / 1000)))

print("THERMAL:")
for r in thermal.face_velocity_sensitivity():
    print(f"   {r['heat_kW']:.0f} kW  mdot {r['mdot_kgs']:.1f}  "
          f"A@25 {r['area_25_ms']:.2f}  A@12 {r['area_hi_ms']:.2f}  A@8 {r['area_lo_ms']:.2f}")
print("   packaged", round(thermal.packaged_core_area_m2(), 2))
fp = thermal.fan_power_W(thermal.cooling_air_flow_kgs(880e3))
print("   fan power kW", round(fp[0] / 1e3, 1), "-", round(fp[1] / 1e3, 1))
print("   burst s:", {v: (None if thermal.coolant_burst_seconds(v) == float('inf')
                          else round(thermal.coolant_burst_seconds(v), 1))
                      for v in (100, 200, 300, 350)})

print("TYRE:", tyre.check())

rows_b, lo, hi = noise.noise_budget()
for a, b in rows_b:
    print(f"   {a:50s} {b}")
print("   att needed", [round(x, 1) for x in noise.required_attenuation_dB()])

ch = validation.chiron_study()
ch2 = validation.chiron_study(mu=1.35)
print("CHIRON mu1.15:", {k: round(v, 2) for k, v in ch["model"].items()},
      {k: round(v, 1) for k, v in ch["error_pct"].items()})
print("CHIRON mu1.35:", {k: round(v, 2) for k, v in ch2["model"].items()},
      {k: round(v, 1) for k, v in ch2["error_pct"].items()})
print("KE 100/350:", round(dynamics.kinetic_energy_MJ(100), 2),
      round(dynamics.kinetic_energy_MJ(350), 1))
