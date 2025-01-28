# config.py

design_inputs = {
    "flight_conditions": {
        "alt": 28000.0,  # ft
        "MN": 0.74,
        "dTs": 0.0,      # degR
    },
    "compressor_design": {
        "fan_PR": 1.75,
        "lpc_PR": 1.2,
        "hpc_PR": 34.48,
        "fan_eff": 0.9,
        "lpc_eff": 0.9243,
        "hpc_eff": 0.907,
    },
    "turbine_design": {
        "hpt_eff": 0.9,
        "lpt_eff": 0.9,
    },
    "other_inputs": {
        "T4_MAX": 1600,  # degK
        "Fn_DES": 10000.0,  # lbf
        "LP_Nmech": 5000,  # rpm
        "HP_Nmech": 13000,  # rpm
        "BPR": 5.9,
        "BPR_bal": 1.60
    }
}

off_design_inputs = {
    "OD_TOfail": {
        "MN": 0.18,
        "alt": 0.0,
        "dTs": 0.0,
        "T4_MAX": 1850.0,
    },
    "OD_TOC": {
        "MN": 0.74,
        "alt": 28000.0,
        "dTs": 0.0,
    },
    "OD_SLS": {
        "MN": 0.00001,
        "alt": 0.0,
        "dTs": 0.0,
    }
}