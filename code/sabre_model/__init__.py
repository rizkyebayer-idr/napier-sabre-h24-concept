# -*- coding: utf-8 -*-
"""Conceptual engineering models for 'Can an Aircraft H-24 Engine Drive a Car?'

Modules
    params    all inputs with R (published) / E (assumed) provenance
    engine    power curve, torque limit, friction and fuel-flow model
    dynamics  road load, traction limit, top speed, acceleration simulation
    mass      mass budget, centre of gravity, static stability factor
    fuel      steady-state fuel consumption
    thermal   heat rejection and cooling-air requirement
    noise     exhaust noise and the silencing budget
"""

__all__ = ["params", "engine", "dynamics", "mass", "fuel", "thermal", "noise"]
__version__ = "1.0"
