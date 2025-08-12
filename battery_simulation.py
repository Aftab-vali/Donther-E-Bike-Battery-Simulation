import numpy as np
import matplotlib.pyplot as plt

def simulate_battery_scenario(
    battery_capacity_kwh=8,
    initial_soc_percent=100,
    total_time_sec=3600,
    dt_sec=1,
    regen_power_profile=None,
    solar_power_w=50,
    consumption_power_w=500
):
    """
    Simulate battery state of charge (SOC) over time considering regenerative braking,
    solar input, and consumption.

    Parameters:
    - battery_capacity_kwh: Battery capacity in kWh (7 to 9 typical)
    - initial_soc_percent: Initial SOC percentage (0 to 100)
    - total_time_sec: Total simulation time in seconds
    - dt_sec: Simulation time step in seconds
    - regen_power_profile: Array of regenerative braking power in Watts for each timestep
                          If None, a sample profile will be generated.
    - solar_power_w: Constant solar panel power input in Watts
    - consumption_power_w: Constant power consumption of bike in Watts

    Returns:
    - time_minutes: Time axis in minutes
    - soc_history_kwh: Battery SOC history in kWh
    - regen_power_profile: Regenerative braking power over time (W)
    - solar_power_profile: Solar power input over time (W)
    - net_power_profile: Net power (regen + solar - consumption) over time (W)
    """
    
    battery_capacity_wh = battery_capacity_kwh * 1000  # convert to Wh
    soc_wh = (initial_soc_percent / 100) * battery_capacity_wh  # initial SOC in Wh

    steps = int(total_time_sec / dt_sec)

    # If regen profile not provided, create a sample sinusoidal regen power to simulate braking cycles
    if regen_power_profile is None:
        time_array = np.linspace(0, total_time_sec, steps)
        # Simulated braking power: sinusoidal between 0 and 150 W, peaks every 10 min
        regen_power_profile = 75 * (1 + np.sin(2 * np.pi * time_array / 600))  # 600 sec = 10 min period
    
    # Solar power input profile (constant for simplicity)
    solar_power_profile = np.full(steps, solar_power_w)

    # Consumption power profile (constant)
    consumption_power_profile = np.full(steps, consumption_power_w)

    soc_history_wh = []
    net_power_profile = []

    for i in range(steps):
        regen_w = regen_power_profile[i]
        solar_w = solar_power_profile[i]
        consumption_w = consumption_power_profile[i]

        # Energy in this timestep (Wh) = Power (W) * (dt in hours)
        energy_in_wh = (regen_w + solar_w) * (dt_sec / 3600)
        energy_out_wh = consumption_w * (dt_sec / 3600)

        # Net energy change = input - output
        net_energy_change_wh = energy_in_wh - energy_out_wh

        # Update SOC
        soc_wh += net_energy_change_wh
        
        # Clamp SOC between 0 and battery capacity
        soc_wh = min(max(soc_wh, 0), battery_capacity_wh)

        # Save SOC and net power (W)
        soc_history_wh.append(soc_wh)
        net_power_profile.append(regen_w + solar_w - consumption_w)

    # Convert SOC history to kWh for readability
    soc_history_kwh = np.array(soc_history_wh) / 1000

    # Time axis in minutes
    time_minutes = np.arange(steps) * dt_sec / 60

    return time_minutes, soc_history_kwh, regen_power_profile, solar_power_profile, np.array(net_power_profile)

# Example usage with parameters matching your Donther specs
battery_capacity = 8  # kWh (choose 7,8 or 9)
initial_soc = 100  # fully charged
simulation_duration_sec = 3600 * 2  # 2 hours simulation
dt = 1  # 1 second timestep
solar_input_watts = 75  # example average solar panel power input
bike_consumption_watts = 450  # average power consumption of the bike

time, soc_kwh, regen_pwr, solar_pwr, net_pwr = simulate_battery_scenario(
    battery_capacity_kwh=battery_capacity,
    initial_soc_percent=initial_soc,
    total_time_sec=simulation_duration_sec,
    dt_sec=dt,
    solar_power_w=solar_input_watts,
    consumption_power_w=bike_consumption_watts
)

# Summary calculations
total_regen_energy_wh = np.sum(regen_pwr) * (dt / 3600)
total_solar_energy_wh = np.sum(solar_pwr) * (dt / 3600)
total_consumed_energy_wh = bike_consumption_watts * (simulation_duration_sec / 3600)
final_soc_kwh = soc_kwh[-1]

print(f"Simulation Time: {simulation_duration_sec/3600:.2f} hours")
print(f"Battery Capacity: {battery_capacity} kWh")
print(f"Initial SOC: {initial_soc}%")
print(f"Total regenerative braking energy input: {total_regen_energy_wh/1000:.3f} kWh")
print(f"Total solar energy input: {total_solar_energy_wh/1000:.3f} kWh")
print(f"Total energy consumed by bike: {total_consumed_energy_wh/1000:.3f} kWh")
print(f"Final battery SOC: {final_soc_kwh:.3f} kWh ({final_soc_kwh/battery_capacity*100:.1f}%)")

# Plot results
plt.figure(figsize=(14, 8))

plt.subplot(3,1,1)
plt.plot(time, soc_kwh, label='Battery SOC (kWh)', color='blue')
plt.ylabel('SOC (kWh)')
plt.title('Battery State of Charge Over Time')
plt.grid(True)
plt.legend()

plt.subplot(3,1,2)
plt.plot(time, regen_pwr, label='Regenerative Braking Power (W)', color='green')
plt.plot(time, solar_pwr, label='Solar Panel Power (W)', color='orange')
plt.ylabel('Power (W)')
plt.title('Power Inputs Over Time')
plt.grid(True)
plt.legend()

plt.subplot(3,1,3)
plt.plot(time, net_pwr, label='Net Power (W) = Regen + Solar - Consumption', color='red')
plt.axhline(0, color='black', linestyle='--')
plt.xlabel('Time (minutes)')
plt.ylabel('Power (W)')
plt.title('Net Power Over Time')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
