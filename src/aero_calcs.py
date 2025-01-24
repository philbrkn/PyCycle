import numpy as np

def calculate_takeoff_distance(W, g, rho, S, CL_max, T, D, L, mu_r, V_LO):
    """
    Calculates the takeoff distance for the C-17 Globemaster III using the given parameters.
    
    Parameters:
        W (float): Aircraft weight in Newtons (N)
        g (float): Acceleration due to gravity (m/s^2)
        rho (float): Air density (kg/m^3)
        S (float): Wing area (m^2)
        CL_max (float): Maximum lift coefficient
        T (float): Total thrust in Newtons (N)
        D (float): Drag force at 0.7 * V_LO in Newtons (N)
        mu_r (float): Coefficient of rolling friction
        V_LO (float): Takeoff velocity in m/s
    
    Returns:
        float: Takeoff distance (meters)
    """    
    # print thrust drag and rolling resistance
    print(f"Thrust: {T}")
    print(f"Drag: {D}")
    print(f"Rolling Resistance: {mu_r * (W - L)}")
    # Compute the denominator using drag and rolling resistance at 0.7 * V_LO
    denominator = T - (D + mu_r * (W - L))
    
    if denominator <= 0:
        raise ValueError("Takeoff is not possible with the given parameters. Check thrust and drag values.")
    
    s_LO = (1.44 * W**2) / (g * rho * S * CL_max * denominator)
    return s_LO

# Given Data
# W_kg = 265352  # Maximum Takeoff Weight (kg)
W_kg = 179169  # Short Takeoff and Landing Weight (kg)
g = 9.81  # Gravity (m/s^2)
rho = 1.225  # Air density at sea level (kg/m^3)
S = 353  # Wing area (m^2)
CL_max_1 = 3.156  # From report
# CL_max_2 = 7.2  # Hypothetical max CL from presentation
Tlbf = 40400  # Total thrust from 4 engines (lbf)
T = 4 * Tlbf * 4.44822  # Total thrust from 4 engines (N)
mu_r = 0.02  # Rolling friction coefficient
V_LO = 52.59  # STOL Takeoff speed in m/s
V_07 = 0.7 * V_LO

# Compute takeoff drag at 0.7 * V_LO
# CL_07 = (2 * (W_kg * g)) / (rho * S * V_07**2)
# CL_07 = 2.938  # From report
CL_07 = 3.156
print(f"CL 07 {CL_07}")
CD_0 = 0.00785  # Zero-lift drag coefficient
e = 1.01  # Oswald efficiency factor
AR = 7.165  # Aspect ratio
Mccormick = 0.837
CD_07 = CD_0 + Mccormick * (CL_07**2) / (np.pi * e * AR)
D_07 = 0.5 * rho * V_07**2 * S * CD_07
L_07 = 0.5 * rho * V_07**2 * S * CL_max_1
# Convert weight to Newtons
W = W_kg * g  # N

# Compute takeoff distances for both CL_max values
s_LO_1 = calculate_takeoff_distance(W, g, rho, S, CL_max_1, T, D_07, L_07, mu_r, V_LO)
# s_LO_2 = calculate_takeoff_distance(W, g, rho, S, CL_max_2, T, D_07, mu_r, V_LO)

print(f"Takeoff distance using CL_max = {CL_max_1}: {s_LO_1:.2f} meters")
# print(f"Takeoff distance using CL_max = {CL_max_2}: {s_LO_2:.2f} meters")
