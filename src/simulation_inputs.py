# ============= 1) DESIGN POINT (CRZ) SETTINGS ===============

TET = 1600.0  # K => ~2880R

DESIGN_PARAMS = {
    # Flight conditions
    "fc.alt": {"val": 28000.0, "units": "ft"},
    "fc.MN": {"val": 0.74, "units": None},
    "fc.dTs": {"val": 0.0, "units": "degR"},  # If you need a delta-temp setting
    # Spool speeds (initial guesses or fixed design speeds)
    "LP_Nmech": {"val": 4666.1, "units": "rpm"},
    "HP_Nmech": {"val": 14705.7, "units": "rpm"},
    # Thrust target (if balancing W to meet Fn_DES)
    "Fn_DES": {"val": 5900.0, "units": "lbf"},
    # Max T4 or TET for design
    "T4_MAX": {"val": TET * 1.8, "units": "degR"},  # 1600 K => degR
    # Bypass Ratio, if you specify it at design
    "splitter.BPR": {"val": 7.5, "units": None},
    # Example compressor/turbine PR or eff
    "fan.PR": {"val": 1.5, "units": None},
    "lpc.PR": {"val": 2.0, "units": None},
    "hpc.PR": {"val": 14.0, "units": None},
    "fan.eff": {"val": 0.8948, "units": None},
    "lpc.eff": {"val": 0.9243, "units": None},
    "hpc.eff": {"val": 0.8707, "units": None},
    "hpt.eff": {"val": 0.8888, "units": None},
    "lpt.eff": {"val": 0.8996, "units": None},
}


# Typical initial balance guesses for the design point
# (the "BalanceComp" variables used in your Cycle)
DESIGN_BALANCE_GUESSES = {
    "CRZ.balance.W": 100.0,  # mass flow guess
    "CRZ.balance.FAR": 0.025,  # fuel-air ratio guess
    "CRZ.balance.lpt_PR": 4.0,  # LPT pressure ratio guess
    "CRZ.balance.hpt_PR": 3.0,  # HPT pressure ratio guess
    "CRZ.fc.balance.Pt": 5.2,  # guess for ambient Pt at fan face
    "CRZ.fc.balance.Tt": 440.0,  # guess for ambient Tt
}

# ============= 2) OFF-DESIGN POINTS ===============
# For each named off-design condition,
# store the flight conditions, T4 or thrust, spool guess, etc.
OFF_DESIGN_PARAMS = {
    "RTO": {
        "fc.alt": {"val": 0.0, "units": "ft"},
        "fc.MN": {"val": 0.25, "units": None},
        "fc.dTs": {"val": 27.0, "units": "degR"},
        # "Fn_target": {"val": 15000.0, "units": "lbf"},
        "T4_MAX": {"val": 3300.0, "units": "degR"},
    },
    # "LDG": {
    #     "fc.alt": {"val": 0.0, "units": "ft"},
    #     "fc.MN": {"val": 0.15, "units": None},
    #     "fc.dTs": {"val": 10.0, "units": "degR"},
    #     "T4_MAX": {"val": 3000.0, "units": "degR"},
    # },
    # "LHR": {
    #     "fc.alt": {"val": 15000.0, "units": "ft"},
    #     "fc.MN": {"val": 0.40, "units": None},
    #     "fc.dTs": {"val": 0.0, "units": "degR"},
    #     "T4_MAX": {"val": 2500.0, "units": "degR"},
    # },
}


# -------------------------------------
#  OFF-DESIGN BALANCE GUESSES / SCALARS
# -------------------------------------
# E.g. spool speeds, BPR, FAR, etc. for each OD point.
OFF_DESIGN_BALANCE_GUESSES = {
    "RTO": {
        "balance.FAR": {"val": 0.03, "units": None},
        "balance.W": {"val": 1000.0, "units": "lbm/s"},
        "balance.BPR": {"val": 9.0, "units": None},
        # "balance.lp_Nmech": {"val": 700.0, "units": "rpm"},
        # "balance.hp_Nmech": {"val": 20000.0, "units": "rpm"},
        # "hpt.PR": {"val": 3.0, "units": None},
        # "lpt.PR": {"val": 4.0, "units": None},
    },
    # "LDG": {
    #     "balance.FAR": {"val": 0.012, "units": None},
    #     "balance.W": {"val": 300.0, "units": "lbm/s"},
    #     "balance.BPR": {"val": 8.0, "units": None},
    #     "balance.lp_Nmech": {"val": 4500.0, "units": "rpm"},
    #     "balance.hp_Nmech": {"val": 14500.0, "units": "rpm"},
    #     # "hpt.PR": {"val": 2.5, "units": None},
    #     # "lpt.PR": {"val": 3.5, "units": None},
    # },
    # "LHR": {
    #     "balance.FAR": {"val": 0.015, "units": None},
    #     "balance.W": {"val": 350.0, "units": "lbm/s"},
    #     "balance.BPR": {"val": 7.5, "units": None},
    #     "balance.lp_Nmech": {"val": 4700.0, "units": "rpm"},
    #     "balance.hp_Nmech": {"val": 14500.0, "units": "rpm"},
    #     "hpt.PR": {"val": 2.8, "units": None},
    #     "lpt.PR": {"val": 3.8, "units": None},
    # },
}

# ============= 3) FLIGHT ENV FOR SWEEPS ===============
FLIGHT_ENV = [
    (0.25, 0),  # Takeoff
    (0.4, 10000),  # Climb
    (0.74, 28000),  # Cruise
    (0.4, 10000),  # Descent
    (0.6, 5000),  # Loiter
]
