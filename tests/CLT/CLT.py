
import numpy as np
import math

class SegmentedLaminateTorsionalModel:
    def __init__(self, plies, E1=135000, E2=10000, nu12=0.3):
        '''
        plies: list of tuples, each (c_r, c_t, h, sweep, t, z, G12, angle)
        '''
        self.plies = plies
        self.E1 = E1
        self.E2 = E2
        self.nu12 = nu12
        self.base_J_geom = self.calculate_geometric_torsional_constant_from_base()

    def calculate_effective_stiffness(self):
        GEJ_total = 0

        for ply in self.plies:
            c_r, c_t, h, sweep, t, z, G12, theta = ply
            A = 0.5 * (c_r + c_t) * h
            G_eff = self.transform_G12(G12, self.E1, self.E2, self.nu12, theta)
            GEJ_i = G_eff * t * A * z**2
            GEJ_total += GEJ_i

        G_E = GEJ_total / self.base_J_geom if self.base_J_geom != 0 else 0
        return G_E, GEJ_total, self.base_J_geom

    def calculate_geometric_torsional_constant_from_base(self):
        '''
        Calculate J_geom based only on the base (first) ply geometry.
        Assumes constant thickness and shape defines the equivalent simplified fin.
        '''
        if not self.plies:
            return 0

        c_r, c_t, h, sweep, t, z, G12, theta = self.plies[0]
        A = 0.5 * (c_r + c_t) * h
        z_squared_avg = np.mean([ply[5]**2 for ply in self.plies])
        total_thickness = sum(ply[4] for ply in self.plies)
        J_geom = total_thickness * A * z_squared_avg
        return J_geom

    @staticmethod
    def transform_G12(G12, E1, E2, nu12, theta_deg):
        theta_rad = math.radians(theta_deg)
        c = math.cos(theta_rad)
        s = math.sin(theta_rad)
        G_eff = G12 * (c**4 + s**4) + 0.5 * (E1 - 2 * nu12 * G12 + E2) * (s**2 * c**2)
        return G_eff
