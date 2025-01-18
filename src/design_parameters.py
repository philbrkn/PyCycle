# design_parameters.py
# Stores all important input parameters for modularity

OPR = 40  # Overall Pressure Ratio
FPR = 1.5  # Fan Pressure Ratio
BPR = 7.5  # Bypass Ratio (Will be optimized)
TET = 1600  # Turbine Entry Temperature (K)
ALT = 28000  # Cruise Altitude (ft)
MN = 0.74  # Mach Number

# Engine Cycle Settings
# --- Engine Cycle Settings ---

SIMULATION_SETTINGS = {
    "fc.alt": ALT,  # Altitude (ft)
    "fc.MN": MN,  # Mach Number
    "fan.PR": FPR,  # Fan Pressure Ratio
    "lpc.PR": 2.0,  # Initial LPC Pressure Ratio (To be optimized)
    "hpc.PR": 14.0,  # Initial HPC Pressure Ratio (To be optimized)
    "fan.eff": 0.8948,  # Fan Efficiency
    "lpc.eff": 0.9243,  # LPC Efficiency
    "hpc.eff": 0.8707,  # HPC Efficiency
    "hpt.eff": 0.8888,  # High-Pressure Turbine Efficiency
    "lpt.eff": 0.8996,  # Low-Pressure Turbine Efficiency
    "T4_MAX": TET*1.8,  # Turbine Entry Temperature (degR = K * 1.8)
    "Fn_DES": 5900.0,  # Design Net Thrust (lbf),
}

ENGINE_DEFAULTS = {
    "splitter.BPR": BPR,  # Bypass Ratio
    "LP_Nmech": 4666.1,  # Low-pressure spool speed (rpm)
    "HP_Nmech": 14705.7,  # High-pressure spool speed (rpm)
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


# --- Initial Guesses for Balances --- #
BALANCE_GUESSES = {
    "DESIGN.balance.FAR": 0.025,  # Fuel-to-air ratio
    "DESIGN.balance.W": 100.0,  # Design point mass flow rate
    "DESIGN.balance.lpt_PR": 4.0,  # Low-pressure turbine pressure ratio
    "DESIGN.balance.hpt_PR": 3.0,  # High-pressure turbine pressure ratio
    "DESIGN.fc.balance.Pt": 5.2,  # Total pressure at fan face
    "DESIGN.fc.balance.Tt": 440.0  # Total temperature at fan face
}

# --- Off-Design Performance Cases ---
OFF_DESIGN_SETTINGS = {
    "OD_full_pwr": {"fc.MN": MN, "fc.alt": ALT, "fc.dTs": 0.0},
    "OD_part_pwr": {"fc.MN": MN, "fc.alt": ALT, "fc.dTs": 0.0},
}

OFF_DESIGN_SIM = {
    "OD_full_pwr": {"T4_MAX": TET*1.8},
    "OD_part_pwr": {"PC": 0.8},
}


# --- Initial Guesses for Off-Design Conditions ---
OFF_DESIGN_GUESSES = {
    "OD_full_pwr": {
        "balance.FAR": 0.02467,
        "balance.W": 300,
        "balance.BPR": 5.105,
        "balance.lp_Nmech": 5000,
        "balance.hp_Nmech": 15000,
        "hpt.PR": 3.0,
        "lpt.PR": 4.0,
        "fan.map.RlineMap": 2.0,
        "lpc.map.RlineMap": 2.0,
        "hpc.map.RlineMap": 2.0
    },
    "OD_part_pwr": {
        "balance.FAR": 0.02467,
        "balance.W": 300,
        "balance.BPR": 5.105,
        "balance.lp_Nmech": 5000,
        "balance.hp_Nmech": 15000,
        "hpt.PR": 3.0,
        "lpt.PR": 4.0,
        "fan.map.RlineMap": 2.0,
        "lpc.map.RlineMap": 2.0,
        "hpc.map.RlineMap": 2.0
    }
}
