class Layer:
    def __init__(self, root_chord_length, tip_chord_length, height, sweep_length, shear_modulus, thickness):
        self.root_chord_length = root_chord_length  # meters
        self.tip_chord_length = tip_chord_length    # meters
        self.height = height                        # meters
        self.sweep_length = sweep_length            # meters
        self.shear_modulus = shear_modulus          # Pascals
        self.thickness = thickness                  # meters


class Homogenisation:
    def __init__(self):
        self.equivalent_fin = None

    def calculate_equivalent_fin(self, layers):
        core = layers[0]
        composite_layers = layers[1:]

        def planform_area(layer):
            return 0.5 * (layer.root_chord_length + layer.tip_chord_length) * layer.height

        core_area = planform_area(core)
        total_volume = core_area * core.thickness
        weighted_G = core.shear_modulus * core_area * core.thickness

        for layer in composite_layers:
            A = planform_area(layer)
            vol = 2 * A * layer.thickness
            total_volume += vol
            weighted_G += 2 * layer.shear_modulus * A * layer.thickness

        G_eq = weighted_G / total_volume
        total_thickness = core.thickness + 2 * sum(layer.thickness for layer in composite_layers)

        def weighted_geom(attr):
            weighted_sum = getattr(core, attr) * core_area * core.thickness
            for layer in composite_layers:
                A = planform_area(layer)
                weighted_sum += 2 * getattr(layer, attr) * A * layer.thickness
            return weighted_sum / total_volume

        self.equivalent_fin = Layer(
            root_chord_length=weighted_geom("root_chord_length"),
            tip_chord_length=weighted_geom("tip_chord_length"),
            height=weighted_geom("height"),
            sweep_length=weighted_geom("sweep_length"),
            shear_modulus=G_eq,
            thickness=total_thickness
        )

        return self.equivalent_fin
    
core = Layer(0.1905, 0.0635, 0.0762, 0.1088, 1e8, 0.002)
layer1 = Layer(0.195, 0.065, 0.077, 0.11, 4e9, 0.0005)
layer2 = Layer(0.188, 0.061, 0.075, 0.107, 5e9, 0.00025)

layers = [core, layer1, layer2]
homogeniser = Homogenisation()
equivalent_fin = homogeniser.calculate_equivalent_fin(layers)

equivalent_fin = homogeniser.calculate_equivalent_fin(layers)

print({
    "root_chord_length (m)": equivalent_fin.root_chord_length,
    "tip_chord_length (m)": equivalent_fin.tip_chord_length,
    "height (m)": equivalent_fin.height,
    "sweep_length (m)": equivalent_fin.sweep_length,
    "shear_modulus (Pa)": equivalent_fin.shear_modulus,
    "total_thickness (m)": equivalent_fin.thickness
})
