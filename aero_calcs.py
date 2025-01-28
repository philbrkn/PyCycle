import numpy as np
import matplotlib.pyplot as plt


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


def calculate_simple_takeoff_distance(W, g, rho, S, CL_max, T, D, L, mu_r):
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

    s_LO = (1.44 * W**2) / (g * rho * S * CL_max * T)
    return s_LO


def calc_sa(Vstall, h_ob=50):
    # calc R:
    R = 6.96*Vstall**2 / 9.81
    theta = np.arccos(1-h_ob/R)

    return R * np.sin(theta)

# Given Data
# W_kg = 265352  # Maximum Takeoff Weight (kg)
W_kg = 179169  # Short Takeoff and Landing Weight (kg)
W_kg *= 0.86**3
g = 9.81  # Gravity (m/s^2)
rho = 1.225  # Air density at sea level (kg/m^3)
S = 353  # Wing area (m^2)
S *= 0.86**2
# CL_max_1 = 3.156  # From report
# CL_max_1 = 7.2  # From report
# CL_max_1 *= 0.9  # Adjusted CL_max for takeoff
CL_max_1 = 3.156  # Lift coefficient during takeoff

Tlbf = 52000  # Total thrust from 4 engines (lbf)
mu_r = 0.02  # Rolling friction coefficient
Vstall = np.sqrt((2 * W_kg * g) / (rho * S * CL_max_1))  # Stall speed in m/s
V_LO = Vstall  # STOL Takeoff speed in m/s
# V_LO = 52.59

print(f"Mass and wing area: {W_kg, S}")
print(f"V_LO: {V_LO}")

V_07 = 0.7 * V_LO # take off velocity at 0.7 * V_LO
W = W_kg * g  # N  # Convert weight to Newtons
T = 4 * Tlbf * 4.44822  # Total thrust from 4 engines (N)

# Compute takeoff drag at 0.7 * V_LO
# CL_07 = (2 * (W_kg * g)) / (rho * S * V_07**2)
# CL_07 = 3.156
CL_groundroll = 3.156  # reference:AIRCRAFT DESIGN AND PERFORMANCE, ANDERSON
CD_0 = 0.00785  # Zero-lift drag coefficient
e = 1.01  # Oswald efficiency factor
AR = 7.165  # Aspect ratio
phi = 0.837  # mccormick factor

CD = CD_0 + phi * (CL_groundroll**2) / (np.pi * e * AR)
# CD = 0.5

# print(f"CL 07 {CL}")
print(f"CD 07 {CD}")

# Drag and lift at 0.7 * V_LO
D_07 = 0.5 * rho * V_07**2 * S * CD
L_07 = 0.5 * rho * V_07**2 * S * CL_max_1

# Compute takeoff distances for both CL_max values
s_LO_1 = calculate_takeoff_distance(W, g, rho, S, CL_max_1, T, D_07, L_07, mu_r, V_LO)
s_LO_2 = calculate_simple_takeoff_distance(W, g, rho, S, CL_max_1, T, D_07, L_07, mu_r)

print(f"Takeoff distance using CL_max = {CL_max_1}: {s_LO_1:.2f} meters")
# print(f"Simple Takeoff distance using CL_max = {CL_max_1}: {s_LO_2:.2f} meters")
# print(f"With safety factor of 1.3 {s_LO_2*1.3}")

sa = calc_sa(Vstall)
print(f"Obstacle clearance distance: {sa} m")
print(f"Total takeoff distance: {s_LO_1 + sa} m")