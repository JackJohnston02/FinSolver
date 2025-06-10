class Layer:
    def __init__(self, root_chord, tip_chord, height, sweep_length, shear_modulus, thickness):
        self.root_chord = root_chord  # meters
        self.tip_chord = tip_chord    # meters
        self.height = height                        # meters
        self.sweep_length = sweep_length            # meters
        self.shear_modulus = shear_modulus          # Pascals
        self.thickness = thickness                  # meters


class Homogenisation:
    def __init__(self):
        self.equivalent_fin = None

    def calculate_equivalent_fin(self, config):
        
        core = config.core

        composite_layers = config.layers

        def planform_area(layer):
            return 0.5 * (layer.root_chord + layer.tip_chord) * layer.height

        core_area = planform_area(core)
        total_volume = core_area * core.thickness
        weighted_G = core.G * core_area * core.thickness

        for layer in composite_layers:
            A = planform_area(layer)
            vol = 2 * A * layer.thickness
            total_volume += vol
            weighted_G += 2 * layer.G * A * layer.thickness

        G_eq = weighted_G / total_volume
        total_thickness = core.thickness + 2 * sum(layer.thickness for layer in composite_layers)

        def weighted_geom(attr):
            weighted_sum = getattr(core, attr) * core_area * core.thickness
            for layer in composite_layers:
                A = planform_area(layer)
                weighted_sum += 2 * getattr(layer, attr) * A * layer.thickness
            return weighted_sum / total_volume

        self.equivalent_fin = Layer(
            root_chord=weighted_geom("root_chord"),
            tip_chord=weighted_geom("tip_chord"),
            height=weighted_geom("height"),
            sweep_length=weighted_geom("sweep_length"),
            shear_modulus=G_eq,
            thickness=total_thickness
        )

        return self.equivalent_fin