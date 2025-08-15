"""
advanced_thermo_storage.py

Thermochemical storage simulation for Ca(OH)2 ↔ CaO + H2O using real ΔH, ΔS.

Generates:
 - equilibrium pressure vs temperature (using Van’t Hoff)
 - temperature vs pressure curve
 - energy density calculation (kWh/kg)
 - round-trip efficiency estimate
 - optional cycle with kinetics placeholder

Run with:
    python advanced_thermo_storage.py
"""

import numpy as np
import matplotlib.pyplot as plt
import os

R = 8.314462618  # J/mol·K

# Real thermodynamic parameters for Ca(OH)2 ↔ CaO + H2O
delta_H = 104.4e3  # J/mol (endothermic)
delta_S = 143.8    # J/mol·K (from entropy values)

molar_mass = 74.09  # g/mol (Ca(OH)2)

def p_eq(T):
    """Equilibrium pressure (bar) at temperature T (K)."""
    ln_p = -delta_H / (R * T) + delta_S / R
    return np.exp(ln_p)

def find_T_for_pressure(p_target):
    Tgrid = np.linspace(300, 1200, 2000)
    pgrid = p_eq(Tgrid)
    diff = np.log(pgrid) - np.log(p_target)
    idx = np.where(np.sign(diff[:-1]) * np.sign(diff[1:]) <= 0)[0]
    if idx.size == 0:
        return None
    i = idx[0]
    t1, t2 = Tgrid[i], Tgrid[i+1]
    f1, f2 = diff[i], diff[i+1]
    return t1 - f1 * (t2 - t1) / (f2 - f1)

def energy_density_per_kg():
    mol_per_kg = 1000.0 / molar_mass
    return delta_H * mol_per_kg / 3.6e6  # kWh/kg

def round_trip_efficiency(mass_kg=10, Cp=900, T_charge=900, T_discharge=500, T_ref=298.15):
    mol_per_kg = 1000/molar_mass
    reaction_energy_J = delta_H * mol_per_kg * mass_kg
    sensible_in = Cp * mass_kg * (T_charge - T_ref)
    sensible_out = Cp * mass_kg * (T_discharge - T_ref)
    energy_in = reaction_energy_J + sensible_in
    energy_out = reaction_energy_J + sensible_out
    return energy_out / energy_in

def run_simulation():
    os.makedirs("outputs", exist_ok=True)
    # Pressure vs temperature
    Tgrid = np.linspace(300, 1200, 500)
    pgrid = p_eq(Tgrid)
    plt.figure()
    plt.semilogy(Tgrid, pgrid)
    plt.xlabel("Temperature (K)")
    plt.ylabel("Equilibrium Pressure (bar)")
    plt.title("Ca(OH)2 ↔ CaO + H2O: p_eq vs T")
    plt.grid(True, which="both", ls="--")
    plt.savefig("outputs/advanced_p_eq_vs_T.png", dpi=200)
    plt.close()

    # Temperature vs pressure
    pressures = np.logspace(-4, 1, 200)
    Teq = [find_T_for_pressure(p) for p in pressures]
    plt.figure()
    plt.semilogx(pressures, Teq)
    plt.xlabel("Pressure (bar)")
    plt.ylabel("Equilibrium Temperature (K)")
    plt.title("Equilibrium Temperature vs Pressure")
    plt.grid(True, which="both", ls="--")
    plt.savefig("outputs/advanced_Teq_vs_p.png", dpi=200)
    plt.close()

    ed = energy_density_per_kg()
    rte = round_trip_efficiency()
    with open("outputs/advanced_summary.txt", "w") as f:
        f.write(f"Energy density (theoretical): {ed:.4f} kWh/kg\n")
        f.write(f"Simplified round-trip efficiency: {rte:.3f}\n")
    print("Advanced simulation complete. Check outputs/.")

if __name__ == "__main__":
    run_simulation()
