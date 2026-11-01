# -*- coding: utf-8 -*-
"""
Regenerate the three figures used in the study.

    python code/make_figures.py        ->  code/figures/fig1_packaging.png
                                          code/figures/fig2_tractive_force.png
                                          code/figures/fig3_fuel_consumption.png

Fig. 1 is a to-scale packaging drawing built from the dimensions in Table III of
the packaging table (all in metres, x rearward from the front-axle line,
z upward).
Fig. 2 and Fig. 3 are direct outputs of dynamics.py and fuel.py.
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sabre_model import dynamics, fuel
from sabre_model import params as p

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

BLUE_DARK = "#1f4e79"
BLUE_MID = "#2e75b6"
BLUE_LIGHT = "#5b9bd5"

# ---------------------------------------------------------------- Fig. 1 data
# (number, x0, z0, length, height, real component?)
SIDE_ITEMS = [
    (4, -0.58, 0.14, 0.79, 0.47, True),    # front radiator module
    (2, 3.54, 0.14, 0.50, 0.26, False),    # clutch / coupling housing
    (3, 4.04, 0.12, 0.85, 0.50, False),    # bespoke transaxle
    (5, 2.60, 0.30, 0.60, 0.40, True),     # side radiator (seen in side view)
    (12, 4.95, 0.30, 0.55, 0.50, False),   # silencers
    (7, 0.72, 0.62, 0.35, 0.40, False),    # driver manikin
    (13, 1.15, 0.20, 0.40, 0.22, False),   # oil tank and cooler
]


def _tag(ax, x, y, num, size=7.5):
    ax.annotate(str(num), (x, y), fontsize=size, ha="center", va="center",
                bbox=dict(boxstyle="circle,pad=0.20", fc="white", ec="k", lw=0.7),
                zorder=6)


def _box(ax, x, y, w, h, real, hatch="///"):
    if real:
        ax.add_patch(Rectangle((x, y), w, h, facecolor="0.82", edgecolor="k",
                               lw=1.0, zorder=3))
    else:
        ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor="0.35",
                               lw=1.0, ls="--", hatch=hatch, zorder=3))


def fig1_packaging(path: str) -> None:
    fig = plt.figure(figsize=(7.2, 7.6), dpi=200)
    ax1 = fig.add_axes([0.02, 0.55, 0.96, 0.40])
    ax2 = fig.add_axes([0.02, 0.06, 0.96, 0.40])

    eng_l, eng_w, eng_h = p.ENGINE_LWH
    eng_x0 = 1.45

    # ------------------------------------------------ (a) side view
    profile = [(0.00, 0.30), (0.35, 0.58), (1.35, 0.92), (2.10, 1.00),
               (3.70, 1.00), (4.75, 0.86), (5.85, 0.60), (5.85, 0.10),
               (0.00, 0.10)]
    ax1.add_patch(Polygon([(x, z) for x, z in profile], closed=True,
                          facecolor="none", edgecolor="k", lw=1.8, zorder=2))

    for x_axle, od, num in ((0.0, p.PACKAGING["tyre_front"][1], 8),
                            (p.WHEELBASE, p.PACKAGING["tyre_rear"][1], 9)):
        r = od / 2.0
        ax1.add_patch(Circle((x_axle, r), r, facecolor="white", edgecolor="k",
                             lw=1.4, zorder=4))
        ax1.add_patch(Circle((x_axle, r), r * 0.55, facecolor="none",
                             edgecolor="0.45", lw=0.8, ls=":", zorder=4))
        _tag(ax1, x_axle, -0.10, num)

    ax1.add_patch(Rectangle((eng_x0, 0.12), eng_l, eng_h, facecolor="#a8c8ec",
                            edgecolor="k", lw=1.4, zorder=3))
    ax1.text(eng_x0 + eng_l / 2, 0.12 + eng_h - 0.10,
             f"Sabre VA envelope\n{eng_l*1000:.0f} × {eng_w*1000:.0f} × {eng_h*1000:.0f}",
             fontsize=8, ha="center", va="top", zorder=5)

    for num, x0, z0, w, h, real in SIDE_ITEMS:
        if num == 7:                      # driver: simple seat outline
            ax1.plot([x0, x0 - 0.10, x0 + 0.18, x0 + 0.30],
                     [z0 - 0.10, z0 + 0.25, z0 + 0.30, z0 + 0.28],
                     color="0.3", lw=1.2, zorder=4)
            _tag(ax1, x0 + 0.10, z0 + 0.55, num)
            continue
        if x0 + w > 5.85:
            continue
        _box(ax1, x0, z0, w, h, real)
        _tag(ax1, x0 + w / 2, z0 + h / 2, num)

    ax1.plot([p.CG_X], [p.CG_Z], marker="o", ms=5, color="k", zorder=6)
    ax1.plot([p.CG_X], [p.CG_Z], marker="+", ms=11, mew=1.6, color="k", zorder=6)
    ax1.text(p.CG_X - 0.22, p.CG_Z, "CG", fontsize=8.5, ha="right", va="center")

    ax1.annotate("", (0.0, -0.30), (p.WHEELBASE, -0.30),
                 arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax1.text(p.WHEELBASE / 2, -0.44, "wheelbase 4000 mm", fontsize=9, ha="center")
    ax1.annotate("", (0.0, -0.78), (5.85, -0.78), arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax1.text(5.85 / 2, -0.92, "overall length 5850 mm", fontsize=9, ha="center")

    ax1.annotate("", (6.15, 0.0), (6.15, 1.40), arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax1.text(6.30, 0.70, "1400", rotation=90, fontsize=9, ha="left", va="center")

    ax1.set_title("(a) Side view", loc="left", fontsize=11)
    ax1.set_xlim(-1.0, 6.9)
    ax1.set_ylim(-1.15, 1.35)
    ax1.set_aspect("equal")
    ax1.axis("off")

    # ------------------------------------------------ (b) plan view
    L, W, track = p.LENGTH, p.WIDTH, p.TRACK
    plan = [(0.00, 0.10), (0.45, 0.00), (L - 0.55, 0.00), (L, 0.22),
            (L, W - 0.22), (L - 0.55, W), (0.45, W), (0.00, W - 0.10)]
    ax2.add_patch(Polygon(plan, closed=True, facecolor="none", edgecolor="k",
                          lw=1.8, zorder=2))

    y_centre_lo = (W - track) / 2.0
    y_centre_hi = W - y_centre_lo
    for y_c, od, width, num in ((y_centre_lo, 0, 0.285, 8),
                                (y_centre_hi, 0, 0.285, 8),
                                (y_centre_lo, 0, 0.355, 9),
                                (y_centre_hi, 0, 0.355, 9)):
        pass  # wheels are drawn below, per axle

    for x_axle, num, width in ((0.0, 8, 0.285), (p.WHEELBASE, 9, 0.355)):
        for y_c in (y_centre_lo, y_centre_hi):
            ax2.add_patch(Rectangle((x_axle - 0.30, y_c - width / 2), 0.60, width,
                                    facecolor="0.55", edgecolor="k", lw=0.9, zorder=4))

    # engine
    ax2.add_patch(Rectangle((eng_x0, (W - eng_w) / 2), eng_l, eng_w,
                            facecolor="#a8c8ec", edgecolor="k", lw=1.4, zorder=3))
    ax2.text(eng_x0 + eng_l / 2, W / 2,
             f"Sabre VA\n{eng_l*1000:.0f} × {eng_w*1000:.0f}",
             fontsize=8.5, ha="center", va="center", zorder=5)

    # side fuel cells, outboard of the cockpit
    for y0 in (0.05, W - 0.05 - 0.30):
        _box(ax2, 0.55, y0, 0.85, 0.30, False)
        _tag(ax2, 0.97, y0 + 0.15, 6)
    # side radiators, ahead of the rear wheels
    for y0 in (0.05, W - 0.05 - 0.47):
        _box(ax2, 2.88, y0, 0.79, 0.47, True)
        _tag(ax2, 3.27, y0 + 0.235, 5)
    # front radiator, low nose
    _box(ax2, 0.05, (W - 0.47) / 2, 0.79, 0.47, True)
    _tag(ax2, 0.44, W / 2, 4)
    # silencers in the rear overhang
    for y0 in (0.60, W - 0.60 - 0.55):
        _box(ax2, 4.95, y0, 0.55, 0.55, False)
        _tag(ax2, 5.22, y0 + 0.275, 12)
    # cockpit / driver
    ax2.plot([1.40, 1.40], [0.10, W - 0.10], "k-", lw=2.2, zorder=4)
    ax2.add_patch(Rectangle((0.86, W / 2 - 0.20), 0.35, 0.40, facecolor="0.78",
                            edgecolor="k", lw=0.8, zorder=4))
    _tag(ax2, 1.03, W / 2, 7)

    ax2.annotate("", (6.30, y_centre_lo), (6.30, y_centre_hi),
                 arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax2.text(6.45, W / 2, "track 1720", rotation=90, fontsize=8.5, va="center")
    ax2.annotate("", (6.90, 0.0), (6.90, W), arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax2.text(7.05, W / 2, "overall width 2120", rotation=90, fontsize=8.5, va="center")

    ax2.plot([1.45, 2.45], [-0.42, -0.42], "k-", lw=3.5, solid_capstyle="butt")
    ax2.text(1.45, -0.62, "1 m", fontsize=9, ha="left")
    ax2.add_patch(Rectangle((3.05, -0.55), 0.22, 0.13, facecolor="0.82",
                            edgecolor="k", lw=1.0))
    ax2.text(3.35, -0.60, "real component (R)", fontsize=8.5, va="center")
    ax2.add_patch(Rectangle((5.05, -0.55), 0.22, 0.13, facecolor="none",
                            edgecolor="0.35", lw=1.0, ls="--", hatch="///"))
    ax2.text(5.35, -0.60, "design envelope (E)", fontsize=8.5, va="center")

    ax2.set_title("(b) Plan view", loc="left", fontsize=11)
    ax2.set_xlim(-0.8, 7.6)
    ax2.set_ylim(-0.95, W + 0.35)
    ax2.set_aspect("equal")
    ax2.axis("off")

    fig.savefig(path)
    plt.close(fig)


# --------------------------------------------------------------------- Fig. 2
def fig2_tractive_force(path: str) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.8), dpi=200)

    v_max = 460.0
    speeds = np.linspace(5.0, v_max / 3.6, 800)
    colours = [BLUE_DARK, BLUE_MID, BLUE_LIGHT, BLUE_LIGHT, "#a6c9ec"]

    for g, colour in enumerate(colours):
        force = np.array([dynamics.tractive_force_N(v, g) for v in speeds]) / 1e3
        ax.plot(speeds * 3.6, force, color=colour, lw=3.0, solid_capstyle="butt")
        flat = force[0]
        idx = int(np.argmax(force < 0.97 * flat))
        ax.annotate(f"G{g+1}", (speeds[idx] * 3.6, force[idx]),
                    textcoords="offset points", xytext=(6, 7), fontsize=12,
                    color="#444444")

    power_line = p.ETA_DRIVELINE * p.P_RATED_W / 1e3
    vv = np.linspace(30.0, v_max, 400)
    ax.plot(vv, power_line / vv, color="0.55", lw=1.6, ls="-.",
            label="Ideal constant-power hyperbola")

    ax.axhline(dynamics.traction_limit_N(0.0) / 1e3, color="#c55a11", lw=2.2, ls=":")
    ax.text(120, dynamics.traction_limit_N(0.0) / 1e3 + 1.2,
            "RWD traction limit\n(static, μ = 1.15)", fontsize=11, color="#333333")

    road = np.array([dynamics.road_load_N(v) for v in speeds]) / 1e3
    ax.plot(speeds * 3.6, road, color="k", lw=2.2, ls="--")
    ax.annotate("Road load", (210, 5.2), fontsize=11)

    ax.axvline(350.0, color="0.35", lw=1.2)
    ax.text(344, 57, "limiter\n350 km/h", ha="right", va="top", fontsize=11,
            color="0.25")

    ax.set_xlim(0, v_max)
    ax.set_ylim(0, 60)
    ax.set_xlabel("Vehicle speed (km/h)", fontsize=13)
    ax.set_ylabel("Force at the wheels (kN)", fontsize=13)
    ax.tick_params(labelsize=12)
    ax.grid(True, color="0.88", lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# --------------------------------------------------------------------- Fig. 3
def fig3_fuel(path: str) -> None:
    curve = fuel.curve(20.0, 305.0, 2.0)
    v = np.array([c[0] for c in curve])
    fc = np.array([c[1] for c in curve])

    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=200)
    ax.axhspan(6.0, 10.0, color="#d9ead3", zorder=0)
    ax.text(310, 8.0, "typical petrol passenger car", ha="right", va="center",
            fontsize=11, color="#3c6e3c")

    ax.plot(v, fc, color=BLUE_MID, lw=3.0)

    for speed, label in [(60, 48), (100, 30), (150, 40), (200, 53), (250, 71), (300, 92)]:
        value = fuel.consumption_at_speed(speed)[0]
        ax.plot([speed], [value], "o", ms=5, color=BLUE_MID)
        ax.annotate(str(label), (speed, value), textcoords="offset points",
                    xytext=(-2, 11), fontsize=11, ha="center")

    ax.set_xlim(10, 320)
    ax.set_ylim(0, 110)
    ax.set_xlabel("Steady speed on level road (km/h)", fontsize=13)
    ax.set_ylabel("Fuel consumption (L/100 km)", fontsize=13)
    ax.tick_params(labelsize=12)
    ax.grid(True, color="0.9", lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    fig1 = os.path.join(OUT, "fig1_packaging.png")
    fig2 = os.path.join(OUT, "fig2_tractive_force.png")
    fig3 = os.path.join(OUT, "fig3_fuel_consumption.png")
    fig1_packaging(fig1)
    fig2_tractive_force(fig2)
    fig3_fuel(fig3)
    for f in (fig1, fig2, fig3):
        print("wrote", f)
