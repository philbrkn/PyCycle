# design_parameters.py
# Stores all important input parameters for modularity

OPR = 40  # Overall Pressure Ratio
FPR = 1.5  # Fan Pressure Ratio
BPR = 7.5  # Bypass Ratio (Will be optimized)
TET = 1600  # Turbine Entry Temperature (K)
ALT = 28000  # Cruise Altitude (ft)
MN = 0.74  # Mach Number
DESIGN_THRUST = 5900.0  # Cruise Net Thrust (lbf)


# --- Engine Design Parameters ---
ENGINE_DEFAULTS = {
    "T4_MAX": TET * 1.8,  # Turbine Entry Temperature (degR = K * 1.8)
    "Fn_DES": DESIGN_THRUST,  # Design Thrust (lbf)
    "fc.alt": ALT,  # Altitude (ft)
    "fc.MN": MN,  # Mach Number
    "LP_Nmech": 4666.1,  # Low-pressure spool speed (rpm)
    "HP_Nmech": 14705.7,  # High-pressure spool speed (rpm)
    "splitter.BPR": BPR,  # Bypass Ratio
}

# Mach Numbers for Different Components
DEFAULT_MN_VALUES = {
    "inlet": 0.7,
    "fan": 0.4578,
    "splitter": {"MN1": 0.3104, "MN2": 0.4518},
    "ducts": {"duct4": 0.3121, "duct6": 0.3563, "duct11": 0.3063, "duct13": 0.4463, "duct15": 0.4589},
    "compressors": {"lpc": 0.3059, "hpc": 0.2442},
    "burner": 0.1025,
    "turbines": {"hpt": 0.3650, "lpt": 0.4127},
    "bleed": {"byp_bld": 0.4489, "bld3": 0.3000},
}
