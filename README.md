# Napier Sabre H-24 — conceptual vehicle model

Calculation code for a first-order engineering assessment of installing a
36.7 L, 24-cylinder Napier Sabre aero engine in a rear-mid-engine land vehicle.

This repository contains **the program only**. It implements the vehicle
dynamics, mass, fuel, thermal and noise models, a validation case against a
production car, and a sensitivity study. Every input is declared in one module
and tagged as either published data or an explicit assumption, so the whole
analysis can be re-run from the stated numbers.

---

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

python code/run_all.py            # verify the model, 42/42 checks
python code/make_figures.py       # regenerate the three figures
```

`run_all.py` exits with a non-zero status if any output drifts away from its
reference value, so it doubles as a regression test.

---

## Module map

```
code/
  sabre_model/
    params.py        every input, tagged R (published) or E (assumed)
    engine.py        power curve, torque limit, FMEP/PMEP, fuel mass flow
    dynamics.py      road load, traction limits, top speed, acceleration run
    mass.py          component mass budget, centre of gravity, stability factor
    fuel.py          steady-state fuel consumption and gear selection
    thermal.py       heat rejection, radiator sizing, coolant thermal inertia
    noise.py         exhaust sound power, A-weighting, silencing budget
    tyre.py          tyre load versus speed-derated capacity
    validation.py    the same models applied to a reference production car
    sensitivity.py   one-at-a-time uncertainty study
  run_all.py             verification against reference values
  revision_checks.py     validation, sensitivity, cooling, tyre and noise runs
  print_key_numbers.py   dump every figure the model produces
  make_figures.py        generate the three figures
```

---

## How the model is built

Nothing is hard-coded outside `params.py`, so a reader can replace any assumption
and re-run the whole analysis. Inputs carry a provenance tag:

* **R** — published or referenced data
* **E** — a design envelope or engineering assumption

The models implemented are:

| Model | Equation |
|---|---|
| Power curve | `P(n) = Pr (x + x² − x³)`, `x = n / nr` |
| Tractive force | `Ft = Te G ηd / rw` |
| Road load | `FR = ½ ρ CD A v² + Crr m g` |
| Top speed | root of `ηd Pr = ½ ρ CD A v³ + Crr m g v` |
| Traction limit | `Fx,max = μ (m g lf / L + m ax h / L)`, solved in closed form because the limit depends on the acceleration it produces |
| Centre of gravity | `xCG = Σ mi xi / Σ mi`, `h = Σ mi zi / Σ mi` |
| Fuel flow | `ṁf = φ [Pb + (FMEP + PMEP) Vd n / 120] / (ηi QLHV)` |
| Exhaust noise | `LW = 10 log10(ηac Pe / W0)`, `Lp = LW − 20 log10 r − 8` |
| Radiator | `Q̇ = ṁa cp ΔTa` |

Two details are worth calling out because they are easy to get wrong:

* **The traction limit is implicit.** Equation (5) makes the limit depend on the
  acceleration it causes. Substituting Newton's second law and solving gives
  `Fx,max = (μ m g lf/L − β FR) / (1 − β)` with `β = μ h / (k L)`. The static
  value under-predicts the limit by about 17 % on this vehicle.
* **The fuel model is a part-load model.** Its friction term extrapolates badly
  at rated speed, so full-load consumption is anchored separately on a
  brake-specific fuel consumption. `fuel.py` uses the friction model below 70 %
  load and the anchor above it.

---

## Uncertainty

`sensitivity.py` perturbs the inputs that are assumed rather than measured —
mass, tyre friction, FMEP coefficient, indicated efficiency, acoustic efficiency
and drag coefficient — one at a time, and reports the resulting ranges for
0–100 km/h, top speed, fuel consumption and noise.

One result is worth keeping in mind when reading the model: while the vehicle is
traction-limited, the 0–100 km/h time is almost independent of mass, because the
force available scales with the same weight that has to be accelerated. It is the
tyre friction coefficient that governs.

---

## Requirements

Python 3.9+ with `numpy`, `matplotlib` and `pymupdf`. See `requirements.txt`.
The model itself needs only the standard library plus `numpy`; `matplotlib` is
used for the figures.

---

## Licence

MIT — see `LICENSE`.
