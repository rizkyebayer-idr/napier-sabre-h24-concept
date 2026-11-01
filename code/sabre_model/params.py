# -*- coding: utf-8 -*-
"""
All numerical inputs for the Napier Sabre car study.

Every constant carries a provenance tag:

    R  = published / referenced data (real component)
    E  = design envelope or engineering assumption made in this study

Changing a value here propagates to every result and figure.
"""

# ---------------------------------------------------------------- engine (R)
P_RATED_W = 1.10e6          # E  de-rated rated power       [W]
N_RATED = 3400.0            # E  rated engine speed         [rpm]
T_LIMIT = 3300.0            # E  electronic torque limit    [N.m]

DISPLACEMENT = 0.03665      # R  36.65 L                    [m3]
BORE = 0.127                # R  127 mm                     [m]
STROKE = 0.121              # R  121 mm                     [m]
N_CYL = 24                  # R
COMPRESSION = 7.0           # R
DRY_MASS_SABRE_VA = 1134.0  # R  published dry mass         [kg]
DRY_MASS_SABRE_IIA = 1071.0  # R  published dry mass        [kg]
ENGINE_LWH = (2.088, 1.016, 1.168)   # R  Sabre VA envelope  [m]
SLEEVE_ROUNDNESS_MM = 0.005          # R  0.0002 in

BSFC_FULL = 1e-7            # E  360 g/kWh at full power    [kg/(W.s)]
Q_LHV = 43.0e6              # R  lower heating value        [J/kg]
ETA_IND = 0.31              # E  indicated efficiency at CR 7:1
PHI_FUEL = 1.20             # E  fuel/air equivalence ratio (rich mixture)
FMEP_A = 0.75               # E  FMEP = a + b (n/1000)^2    [bar]
FMEP_B = 0.20
PMEP_LIGHT = 0.60           # E  pumping losses at light load [bar]
PMEP_FULL = 0.00            # E  pumping losses at full load  [bar]

# --------------------------------------------------------------- vehicle (E)
MASS_KG = 3225.0            # from mass budget (see mass.py), incl. driver
WHEELBASE = 4.00
LENGTH = 5.85
WIDTH = 2.12
HEIGHT = 1.40
TRACK = 1.72
CG_X = 2.38                 # behind front axle, from mass budget
CG_Z = 0.54                 # from mass budget

R_TYRE = 0.345              # E  dynamic rolling radius, 355/25 ZR21
CD = 0.38
FRONTAL_AREA = 2.43
C_RR = 0.013
RHO_AIR = 1.18
MU = 1.15
ETA_DRIVELINE = 0.88

GEAR_RATIOS = (4.91, 3.47, 2.46, 1.74, 1.26)   # overall, E
SHIFT_RPM = 3400.0
SHIFT_TIME = 0.25           # E  zero-torque interval per shift [s]
ROT_MASS_FACTOR = 1.06      # E
DT = 0.01                   # E  integration step [s]
LAUNCH_RPM = 2000.0         # E  clutch-slip launch speed [rpm]
V_GOVERNED = 350.0 / 3.6    # E  governed top speed [m/s]

# ------------------------------------------------------------------- fuel (E)
RHO_FUEL = 0.745            # kg/L  (98 RON petrol)
FUEL_MIN_RPM = 900.0
IDLE_RPM = 800.0

# ------------------------------------------------------------------ noise (E)
ETA_ACOUSTIC = (3e-6, 3e-5)  # acoustic conversion efficiency bracket
W_REF = 1e-12                # reference sound power [W]
R_PASSBY = 7.5               # pass-by distance [m]
PASSBY_LIMIT_DBA = 72.0      # EU 540/2014, PMR > 200 kW/t, phase 3

# ---------------------------------------------------------------- thermal (E)
HEAT_FRACTION = (0.60, 0.80)  # of brake power rejected to coolant+oil
CP_AIR = 1005.0               # J/kg/K
DELTA_T_AIR = 30.0            # K across radiator core
FACE_VELOCITY = 25.0          # m/s, as originally assumed (optimistic)
FACE_VELOCITY_RANGE = (8.0, 12.0)   # m/s, realistic vehicle practice
CORE_PRESSURE_DROP = (250.0, 400.0)  # Pa at the realistic face velocities
FAN_EFFICIENCY = 0.55
COOLANT_MASS = 40.0           # kg water/glycol in the circuit
COOLANT_CP = 3500.0           # J/kg/K
AMBIENT_C = 30.0              # tropical ambient in Batam
COOLANT_LIMIT_C = 105.0       # pressurised system limit

# ------------------------------------------------------------------- tyre (E)
TYRE_STATIC_LOAD_LIMIT = 975.0   # kg, load index 107 for 355/25 ZR21
TYRE_SPEED_DERATE = (0.80, 0.90)  # permissible load factor at 350 km/h

# ------------------------------------------------------- mass budget (table) (E)
# (label, mass kg, x m behind front axle, z m above ground)
MASS_ITEMS = [
    ("Engine (1,134 kg dry), coupling gear case, flywheel, adaptor", 1180, 2.49, 0.70),
    ("Clutch, bespoke transaxle, half-shafts",                          400, 4.17, 0.42),
    ("Front radiator module and fans",                                   55, -0.58, 0.36),
    ("Side radiator modules and fans",                                  110, 2.95, 0.49),
    ("Coolant, pipework, header tank",                                   50, 1.60, 0.45),
    ("Oil tank, oil cooler, oil",                                        75, 1.75, 0.40),
    ("Exhaust manifolds and silencers",                                 110, 3.60, 0.72),
    ("Steel space frame and roll structure",                            400, 2.05, 0.45),
    ("Composite body and aero devices",                                 150, 2.05, 0.70),
    ("Suspension, wheels, tyres, brakes",                               340, 2.24, 0.35),
    ("Fuel (150 L), two cells, pumps",                                  150, 0.83, 0.32),
    ("Electrical, starters, ECU, battery",                               65, 0.20, 0.45),
    ("Seat, controls, fire system",                                      60, 0.85, 0.45),
    ("Driver",                                                           80, 0.95, 0.45),
]

# ------------------------------------------------------------ packaging (R/E)
PACKAGING = {
    "engine": (1, 2.088, 1.016, True),
    "clutch": (2, 0.500, 0.260, False),
    "transaxle": (3, 0.850, 0.600, False),
    "radiator": (4, 0.794, 0.470, True),
    "side_radiator": (5, 0.794, 0.470, True),
    "fuel_cell": (6, 0.850, 0.300, False),
    "tyre_front": (8, 0.679, 0.285, True),
    "tyre_rear": (9, 0.711, 0.355, True),
    "silencer": (12, 0.500, 0.550, False),
}
