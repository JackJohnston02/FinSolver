import numpy as np
from scipy.linalg import eig
import matplotlib.pyplot as plt
import yaml

# === Load from YAML ===
with open('tests/supersonic_flutter_method/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

fin_geometry = config['fin_geometry']
layers = config['layers']
air = config['air']

# === Derived Geometry ===
chord_root = float(fin_geometry['root_chord'])
chord_tip = float(fin_geometry['tip_chord'])
chord = 0.5 * (chord_root + chord_tip)
height = float(fin_geometry['height'])
span = height
area = 0.5 * (chord_root + chord_tip) * span

# === Structural Properties ===
lam_thickness = 2 * sum(float(l['material']['thickness']) for l in layers.values()) + float(fin_geometry['thickness_core'])
mass_total = 0.0
I_pitch = 0.0
EI_total = 0.0
G_weighted = 0.0
G_volume = 0.0

for l in layers.values():
    t = float(l['material']['thickness'])
    rho = float(l['material']['density'])
    E = 0.5 * (float(l['material']['E_warp']) + float(l['material']['E_weft']))
    G = float(l['material']['G12'])
    A = 0.5 * (float(l['geometry']['root_chord']) + float(l['geometry']['tip_chord'])) * float(l['geometry']['height'])

    mass_total += 2 * A * t * rho
    I_pitch += 2 * (1/12) * rho * A * t * chord**2
    EI_total += 2 * E * t * (chord**3) / 12  # classic I = bt^3/12 for bending
    G_weighted += G * t
    G_volume += t

# Add core contribution
core_rho = float(config['core']['density'])
core_E = float(config['core']['E'])
core_G = float(config['core']['G'])
core_thk = float(fin_geometry['thickness_core'])
core_area = 0.5 * (chord_root + chord_tip) * height
mass_total += core_area * core_thk * core_rho
I_pitch += (1/12) * core_rho * core_area * core_thk * chord**2
EI_total += core_E * core_thk * (chord**3) / 12
G_weighted += core_G * core_thk
G_volume += core_thk

G_avg = G_weighted / G_volume

# Updated torsional constant for rectangular section (thin shell approx)
t = core_thk + 2 * sum(float(l['material']['thickness']) for l in layers.values())
J = (1/3) * t * (chord ** 3) / (1 + (chord / span))
GJ = G_avg * J

# Heave and torsion stiffness
k_h = 3 * EI_total / (span**3)
k_theta = GJ / span

# Aero properties
rho_air = float(air['density'])
a0 = float(air.get('speed_of_sound', 340))
x_cp = 0.3 * chord

# === Matrices ===
M = np.array([[mass_total, 0],
              [0, I_pitch]])

K = np.array([[k_h, 0],
              [0, k_theta]])

# === Sweep Velocity ===
U_range = np.linspace(50, 6000, 600)
damping = []
frequencies = []
flutter_speed = None

for U in U_range:
    q_inf = 0.5 * rho_air * U**2

    Ka = q_inf * np.array([[area / a0, area * x_cp / a0],
                           [area * x_cp / a0, area * x_cp**2 / a0]])

    A = K - Ka
    eigvals, _ = eig(A, M)

    if U == 50:
        print(f"[DEBUG] q_inf: {q_inf:.2f}")
        print(f"[DEBUG] Eigenvalues at {U} m/s: {eigvals}")

    omegas = np.sqrt(np.real(eigvals))
    damping_ratios = -np.real(eigvals) / (2 * np.abs(eigvals))

    damping.append(np.min(damping_ratios))
    frequencies.append(np.min(omegas))

    real_parts = np.real(eigvals)
    if flutter_speed is None and np.any(real_parts < 0):
        flutter_speed = U


# === Plot ===
plt.figure()
plt.plot(U_range, damping, label="Minimum Damping Ratio")
plt.axhline(0, color='k', linestyle='--')
if flutter_speed:
    plt.axvline(flutter_speed, color='r', linestyle='--', label=f"Flutter @ {flutter_speed:.1f} m/s")
plt.xlabel("Freestream Velocity [m/s]")
plt.ylabel("Damping Ratio")
plt.title("2DOF Aeroelastic Flutter Prediction")
plt.legend()
plt.grid(True)
plt.show()

# === Output Summary ===
print("Mass (estimated): {:.3f} kg".format(mass_total))
print("Torsional Inertia (I): {:.3e} kg·m²".format(I_pitch))
print("Heave Stiffness k_h: {:.2e} N/m".format(k_h))
print("Pitch Stiffness k_theta: {:.2e} Nm/rad".format(k_theta))
print("Torsional Constant J: {:.2e} m^4".format(J))
print("Torsional Stiffness GJ: {:.2e} Nm^2".format(GJ))

if flutter_speed:
    print("Estimated Flutter Speed: {:.2f} m/s (Mach {:.2f})".format(flutter_speed, flutter_speed / a0))
else:
    print("No flutter detected up to {:.0f} m/s (Mach {:.1f})".format(U_range[-1], U_range[-1] / a0))
