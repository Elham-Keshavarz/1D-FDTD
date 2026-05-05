"""
1D FDTD Acoustic Wave Simulation with:
1) Mur 1st-order Absorbing Boundary Condition
2) Reflection/Transmission Coefficient Calculation

Author: Elham Keshavarz Arshadi
Date: May 2026
"""

import numpy as np
import matplotlib.pyplot as plt

# ============================
# Simulation parameters (stable)
# ============================
nx = 200                # number of spatial grid points
dx = 0.01               # spatial step (m)
c0 = 340.0              # speed of sound in left medium (air)
c1 = 1500.0             # speed of sound in right medium (water-like)
c_max = c1              # max speed of sound for CFL condition
dt = 0.2 * dx / c_max   # time step (safety factor 0.2, ensures stability)
duration = 0.008        # total simulation time (s)
nt = int(duration / dt) # number of time steps

# Two-layer medium: interface at 60% of the grid
interface = int(nx * 0.6)
c = np.ones(nx) * c0
c[interface:] = c1      # assign higher speed to the right region

# Pressure fields: current, previous, next time steps
p = np.zeros(nx)
p_prev = np.zeros(nx)
p_next = np.zeros(nx)

# Source: Gaussian pulse (weak, short duration)
source_pos = 15         # grid index of source
source_width = 8        # width of Gaussian
source_amp = 0.2        # amplitude (small to avoid instability)

# ============================
# Main time loop (with Mur ABC)
# ============================
for n in range(nt):
    # Update interior points using the discretized wave equation
    for i in range(1, nx-1):
        # Second spatial derivative (central difference)
        d2p_dx2 = (p[i+1] - 2*p[i] + p[i-1]) / (dx*dx)
        # Finite-difference time-domain update
        p_next[i] = 2*p[i] - p_prev[i] + (c[i]*dt)**2 * d2p_dx2
    
    # Add source (only during first 60 time steps)
    if n < 60:
        p_next[source_pos] += source_amp * np.exp(-((n - 20) / source_width)**2)
    
    # Mur 1st-order absorbing boundary condition at left boundary (x=0)
    # This prevents artificial reflections from the left edge
    p_next[0] = p_next[1] - (c[0]*dt - dx)/(c[0]*dt + dx) * (p_next[1] - p[0])
    
    # Mur ABC at right boundary (x = (nx-1)*dx)
    p_next[-1] = p_next[-2] - (c[-1]*dt - dx)/(c[-1]*dt + dx) * (p_next[-2] - p[-1])
    
    # Shift time steps forward
    p_prev[:] = p[:]
    p[:] = p_next[:]

# ============================
# Calculate reflection and transmission coefficients from simulation
# ============================
incident_peak = np.max(p[:interface-10])           # maximum pressure before interface
reflected_peak = np.max(np.abs(p[5:interface-10])) # maximum reflected amplitude
transmitted_peak = np.max(p[interface+10:])        # maximum transmitted amplitude

R_sim = reflected_peak / incident_peak if incident_peak != 0 else 0
T_sim = transmitted_peak / incident_peak if incident_peak != 0 else 0

# Theoretical coefficients based on impedance (density assumed equal)
Z0, Z1 = c0, c1
R_th = (Z1 - Z0) / (Z1 + Z0)
T_th = 2 * Z1 / (Z1 + Z0)

# ============================
# Plot results (4 subplots)
# ============================
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Subplot 1: speed of sound profile
ax = axes[0,0]
ax.plot(np.arange(nx)*dx, c, 'b-')
ax.axvline(x=interface*dx, color='r', linestyle='--')
ax.set_title('Speed of sound profile')
ax.set_xlabel('Position (m)')
ax.set_ylabel('Speed (m/s)')
ax.grid(True)

# Subplot 2: final pressure field
ax = axes[0,1]
ax.plot(np.arange(nx)*dx, p, 'g-')
ax.axvline(x=interface*dx, color='r', linestyle='--')
ax.set_title('Final pressure field (reflection & transmission)')
ax.set_xlabel('Position (m)')
ax.set_ylabel('Pressure')
ax.grid(True)

# Subplot 3: bar chart comparing simulated and theoretical coefficients
ax = axes[1,0]
labels = ['Reflection', 'Transmission']
sim_vals = [R_sim, T_sim]
th_vals = [R_th, T_th]
x = np.arange(len(labels))
width = 0.35
ax.bar(x - width/2, sim_vals, width, label='Simulated')
ax.bar(x + width/2, th_vals, width, label='Theoretical')
ax.set_ylabel('Coefficient')
ax.set_title('Reflection & Transmission Coefficients')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
ax.grid(True, axis='y')

# Subplot 4: text box with coefficient values
ax = axes[1,1]
ax.axis('off')
textstr = f'Simulated R = {R_sim:.3f}\nTheoretical R = {R_th:.3f}\n\nSimulated T = {T_sim:.3f}\nTheoretical T = {T_th:.3f}'
ax.text(0.1, 0.5, textstr, fontsize=14, verticalalignment='center')
ax.set_title('Coefficient values')

plt.tight_layout()
plt.savefig('fdtd.png', dpi=150)
plt.show()

# Print coefficients to console
print(f"Reflection coefficient - Simulated: {R_sim:.3f}, Theoretical: {R_th:.3f}")
print(f"Transmission coefficient - Simulated: {T_sim:.3f}, Theoretical: {T_th:.3f}")