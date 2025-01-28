import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Constants and Parameters
rho = 1.225  # Air density at sea level (kg/m^3)
S = 353  # Wing area (m^2)
CL = 2.938  # Lift coefficient during takeoff
Cdo = 0.00785  # Zero-lift drag coefficient
AR = 7.165  # Aspect Ratio
e0 = 1.01  # Oswald's efficiency factor
K1 = 1 / (np.pi * AR * e0)  # Induced drag factor
mu_r = 0.02  # Coefficient of rolling friction
g = 9.81  # Gravity (m/s^2)

# Weight
MTOW_kg = 265352  # Maximum Take-Off Weight (kg)
W = MTOW_kg * g  # Weight in Newtons
m = W / g  # Mass in kg

# Thrust
thrust_per_engine = 179886.082  # N
num_engines = 4
T_total = thrust_per_engine * num_engines  # Total Thrust (N)

# Takeoff Velocity
V_takeoff = 64  # m/s


# Define the differential equations
def equations(t, y):
    V, s = y  # y = [Velocity, Distance]

    # Calculate Lift
    L = 0.5 * rho * V**2 * S * CL

    # Ensure Lift does not exceed Weight
    L = min(L, W)

    # Calculate Drag
    D = 0.5 * rho * V**2 * S * (Cdo + K1 * CL**2)

    # Calculate Friction
    R = mu_r * (W - L)

    # Calculate Net Force
    F_net = T_total - D - R

    # Acceleration
    a = F_net / m  # m/s^2

    # Differential equations
    dV_dt = a
    ds_dt = V

    return [dV_dt, ds_dt]


# Initial Conditions
V0 = 0  # Initial velocity (m/s)
s0 = 0  # Initial distance (m)
y0 = [V0, s0]

# Time Span for Integration
# Estimate maximum time needed; e.g., 100 seconds
t_span = (0, 100)
# Time evaluation points (dense for better resolution)
t_eval = np.linspace(t_span[0], t_span[1], 10000)

# Solve the ODEs
solution = solve_ivp(equations, t_span, y0, t_eval=t_eval, method="RK45")

# Extract results
V = solution.y[0]  # Velocity (m/s)
s = solution.y[1]  # Distance (m)

# Limit the data up to takeoff
takeoff_index = np.argmax(V >= V_takeoff)
if V[takeoff_index] < V_takeoff:
    takeoff_index = len(V) - 1  # Take all data if takeoff speed not reached

V = V[:takeoff_index]
s = s[:takeoff_index]

print(f"Takeoff Distance: {s[-1]:.2f} m")

# Recalculate Forces at each distance
L = 0.5 * rho * V**2 * S * CL
L = np.minimum(L, W)  # Ensure Lift does not exceed Weight
D = 0.5 * rho * V**2 * S * (Cdo + K1 * CL**2)
R = mu_r * (W - L)
D_plus_R = D + R

# Plotting Forces vs Runway Length
plt.figure(figsize=(14, 8))
plt.plot(s, L, label="Lift (L)", color="blue")
plt.plot(s, D, label="Drag (D)", color="red")
plt.plot(s, [T_total] * len(s), label="Thrust (T)", color="green", linestyle="--")
plt.plot(s, R, label="Friction (R)", color="orange")
plt.plot(s, D_plus_R, label="Drag + Friction (D + R)", color="purple")

plt.title("Forces on C-17 Aircraft During Takeoff vs Runway Length")
plt.xlabel("Runway Length (m)")
plt.ylabel("Force (N)")
plt.legend()
plt.grid(True)
plt.xlim(0, max(s))
plt.ylim(0, max(T_total, max(L)) * 1.1)

plt.show()

# Optional: Plot Velocity vs Runway Length
plt.figure(figsize=(14, 6))
plt.plot(s, V, label="Velocity (V)", color="black")
plt.title("Velocity vs Runway Length During Takeoff")
plt.xlabel("Runway Length (m)")
plt.ylabel("Velocity (m/s)")
plt.legend()
plt.grid(True)
plt.xlim(0, max(s))
plt.ylim(0, max(V) * 1.1)
plt.show()
