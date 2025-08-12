import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Parameters specific to M1 motor setup
rotor_inertia = 0.004  # kg*m^2 (slightly smaller motor at front wheel)
num_poles = 12  # 6 pole pairs
resistance = 0.08  # Ohms (higher resistance due to smaller windings)
inductance = 0.0003  # H
emf_constant = 0.12  # V/(rad/s) lower due to smaller winding area
load_torque = 0.03  # Nm, braking load torque

# Initial conditions for regenerative braking simulation
initial_speed = 83.77  # rad/s (corresponds to 40 km/h on 0.3m radius wheel)
initial_currents = [0.0, 0.0, 0.0]

# Back EMF generation function based on motor rotation
def back_emf(speed):
    theta = speed * np.linspace(0, 1, 3) * num_poles  # simulate phase offset
    emf = emf_constant * np.sin(theta + np.array([0, -2*np.pi/3, 2*np.pi/3]))
    return emf

# Dynamic model of the BLDC generator in M1
def bldc_gen_model(t, y):
    speed = y[0]
    currents = y[1:]

    emf = back_emf(speed)
    torque = np.dot(currents, emf)
    d_speed_dt = (torque - load_torque) / rotor_inertia
    d_currents_dt = (emf - resistance * currents) / inductance

    return [d_speed_dt] + list(d_currents_dt)

# Time for simulation
t_span = (0, 1.5)
t_eval = np.linspace(t_span[0], t_span[1], 1000)

# Solving the model
sol = solve_ivp(bldc_gen_model, t_span, [initial_speed] + initial_currents, t_eval=t_eval)
speed = sol.y[0]
currents = sol.y[1:]

# Rectified DC output from 3-phase currents
def rectify_dc(ia, ib, ic):
    return (np.maximum(ia, 0) + np.maximum(ib, 0) + np.maximum(ic, 0)) / 3

dc_voltage = rectify_dc(currents[0], currents[1], currents[2])

# Plotting results
plt.figure(figsize=(14, 10))

plt.subplot(3, 1, 1)
plt.plot(sol.t, speed, label="Rotor Speed (rad/s)")
plt.title("Rotor Speed over Time (M1 Motor)")
plt.xlabel("Time (s)")
plt.ylabel("Speed (rad/s)")
plt.grid(True)
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(sol.t, currents[0], label="Phase A")
plt.plot(sol.t, currents[1], label="Phase B")
plt.plot(sol.t, currents[2], label="Phase C")
plt.title("Phase Currents")
plt.xlabel("Time (s)")
plt.ylabel("Current (A)")
plt.grid(True)
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(sol.t, dc_voltage, color='green', label="Rectified DC Output")
plt.title("DC Voltage from M1 Generator")
plt.xlabel("Time (s)")
plt.ylabel("DC Voltage (V)")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
