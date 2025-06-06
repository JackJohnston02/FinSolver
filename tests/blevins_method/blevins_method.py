import yaml
import matplotlib.pyplot as plt
import math

# Load YAML configuration
with open('tests/blevins_method/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

fin_geometry = config['fin_geometry']
layers = config['layers']

# Utility to compute trapezoid corners with root chord centered at (0, 0)
def compute_trapezoid_vertices(root_chord, tip_chord, height, sweep):
    y_bottom = 0.0
    y_top = height

    x_root_le = -root_chord / 2
    x_root_te = root_chord / 2

    x_tip_le = x_root_le + sweep
    x_tip_te = x_tip_le + tip_chord

    return [
        (x_root_le, y_bottom),
        (x_root_te, y_bottom),
        (x_tip_te, y_top),
        (x_tip_le, y_top)
    ]

# Calculate area, centroid, and moment of inertia about its own centroid
def trapezoid_area_centroid_inertia(root_chord, tip_chord, height):
    area = 0.5 * (root_chord + tip_chord) * height
    centroid_y = height / 3 * (2 * root_chord + tip_chord) / (root_chord + tip_chord)
    I_centroid = (height**3 / 36) * (root_chord**2 + 4 * root_chord * tip_chord + tip_chord**2) / (root_chord + tip_chord)
    return area, centroid_y, I_centroid

# Estimate flutter velocity using Blevins-style formula
def estimate_flutter_velocity(EI, rho_air, S_ref, e_ref):
    k = 0.05  # reduced empirical constant
    return math.sqrt((k * EI) / (rho_air * S_ref * e_ref**2))

# Plotting setup
fig, ax = plt.subplots()
colors = ['skyblue', 'salmon', 'lightgreen']

layer_data = []

# Plot each layer with root chord centered at y=0
for i, (layer_name, layer_info) in enumerate(layers.items()):
    geom = layer_info['geometry']
    root = float(geom['root_chord'])
    tip = float(geom['tip_chord'])
    height = float(geom['height'])
    sweep = float(geom['sweep_length'])

    verts = compute_trapezoid_vertices(root, tip, height, sweep)
    poly = plt.Polygon(verts, closed=True, facecolor=colors[i % len(colors)], alpha=0.6, label=layer_name)
    ax.add_patch(poly)

    area, centroid, I_centroid = trapezoid_area_centroid_inertia(root, tip, height)
    E_warp = float(layer_info['material']['E_warp'])
    E_weft = float(layer_info['material']['E_weft'])
    E_eq = 0.5 * (E_warp + E_weft)
    layer_data.append({
        "name": layer_name,
        "area": area,
        "centroid_y": centroid,
        "I_centroid": I_centroid,
        "E_eq": E_eq
    })

# Plot core geometry with root chord also at y=0
core_root = float(fin_geometry['root_chord'])
core_tip = float(fin_geometry['tip_chord'])
core_height = float(fin_geometry['height'])
core_sweep = float(fin_geometry['sweep_length'])

core_verts = compute_trapezoid_vertices(core_root, core_tip, core_height, core_sweep)
core_poly = plt.Polygon(core_verts, closed=True, facecolor='gray', alpha=0.4, label='core')
ax.add_patch(core_poly)

core_area, core_centroid, core_I = trapezoid_area_centroid_inertia(core_root, core_tip, core_height)
core_E = float(fin_geometry['E']) if 'E' in fin_geometry else 1e9
layer_data.append({
    "name": "core",
    "area": core_area,
    "centroid_y": core_centroid,
    "I_centroid": core_I,
    "E_eq": core_E
})

# Calculate global centroid (area-weighted)
total_area = sum(layer["area"] for layer in layer_data)
global_centroid = sum(layer["area"] * layer["centroid_y"] for layer in layer_data) / total_area

# Calculate total moment of inertia using parallel axis theorem and bending stiffness EI
total_I = 0.0
total_EI = 0.0

for layer in layer_data:
    dy = layer["centroid_y"] - global_centroid
    I_adj = layer["I_centroid"] + layer["area"] * dy**2
    EI = layer["E_eq"] * I_adj
    total_I += I_adj
    total_EI += EI
    layer["I_adjusted"] = I_adj
    layer["EI"] = EI

# Estimate flutter speed
rho_air = 1.225  # kg/m^3 at sea level
span = core_height  # fin height
mean_chord = 0.5 * (core_root + core_tip)
S_ref = span * mean_chord
e_ref = mean_chord / 2  # assume center of pressure at half chord
flutter_speed = estimate_flutter_velocity(total_EI, rho_air, S_ref, e_ref)

# Debugging output
print("\nDEBUGGING OUTPUT:")
print(f"rho_air = {rho_air:.3f} kg/m^3")
print(f"span = {span:.3f} m")
print(f"mean_chord = {mean_chord:.3f} m")
print(f"S_ref = {S_ref:.6f} m^2")
print(f"e_ref = {e_ref:.3f} m")
print(f"EI_total = {total_EI:.2e} Nm^2")
print(f"Flutter speed calculation = sqrt((k * EI) / (rho * S * e^2))")

# Output results
print("\nLayer Centroids, Areas, Inertias, and Bending Stiffness:")
for layer in layer_data:
    print(f"{layer['name']}: Area = {layer['area']:.6f} m^2, Centroid_y = {layer['centroid_y']:.6f} m, I = {layer['I_adjusted']:.8f} m^4, EI = {layer['EI']:.2e} Nm^2")

print(f"\nGlobal Laminate Centroid (from root edge): {global_centroid:.6f} m")
print(f"Total Moment of Inertia about Global Centroid: {total_I:.8f} m^4")
print(f"Total Bending Stiffness (EI): {total_EI:.2e} Nm^2")
print(f"\nEstimated Flutter Velocity (Blevins method): {flutter_speed:.2f} m/s")

# Finalize plot
ax.set_aspect('equal')
ax.set_xlabel('Chordwise direction (x) [m]')
ax.set_ylabel('Spanwise direction (y) [m]')
ax.set_title('Fin Cross Section Geometry')
ax.legend()
plt.grid(True)

# Recalculate plot limits based on patches
all_verts = []
for patch in ax.patches:
    all_verts.extend(patch.get_xy())

xs, ys = zip(*all_verts)
margin = 0.01
ax.set_xlim(min(xs) - margin, max(xs) + margin)
ax.set_ylim(min(ys) - margin, max(ys) + margin)

# Save and display
plt.savefig("tests/blevins_method/diagram.png", dpi=300)
plt.show()
