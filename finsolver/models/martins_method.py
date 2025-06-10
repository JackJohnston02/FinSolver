import numpy as np
import matplotlib.pyplot as plt

class FlutterAnalysisMartinsMethod:

    def __init__(self):
        min_altitude = 0        # m
        max_altitude = 10000    # m
        altitude_resolution = 1 # m
        self.n = 1 + (max_altitude - min_altitude) // altitude_resolution
        self.altitude_range = np.linspace(min_altitude, max_altitude, self.n)

        self.safety_margin = 25/100 # Safety margin in fraction. 25% is reccomended

    def analyse_fin(self, fin):

        results = {
            "altitude": [None] * self.n,
            "flutter_velocity": [None] * self.n,
            "safe_velocity": [None] * self.n
        }

        for i in range(self.n):
            
            altitude = self.altitude_range[i]

            T = self.calculate_temperature_at_altitude(altitude)
            speed_of_sound = self.calculate_speed_of_sound(T)
            air_pressure = self.calculate_air_pressure(T)

            flutter_velocity = self.calculate_flutter_velocity(speed_of_sound, fin.shear_modulus, fin.height, fin.thickness, fin.root_chord, air_pressure, fin.sweep_length, fin.tip_chord)

            results["altitude"][i] = altitude
            results["flutter_velocity"][i] = flutter_velocity
            results["safe_velocity"][i] = flutter_velocity - (flutter_velocity * self.safety_margin)

            #print(f"[DEBUG] Altitude: {altitude}, Flutter velocity: {flutter_velocity}")
        
        self.plot_flutter_velocity_at_altitude(results)



    @staticmethod
    def calculate_flutter_velocity(speed_of_sound, shear_modulus, height, fin_thickness, root_chord_length, air_pressure, sweep_length, tip_chord_length):
        '''
        Calculate the flutter velocity (v_f) in m/s.
        '''

        p_0 = 101.325e3 # Pressure at sea level in Pa

        def calculate_epsilon(tip_chord_length, root_chord_length, sweep_length):
            TC = tip_chord_length
            RC = root_chord_length
            m = sweep_length

            C_x = ((2 * TC * m) + TC**2 + (m * RC) + (TC * RC) + RC**2)/(3 * (TC + RC))

            return (C_x / RC) - 0.25

        def calculate_denominator_constant(epsilon, p_0):
            kappa = 1.4 # adiabatic index for air
            return (24 * epsilon * kappa * p_0)/(np.pi)
        
        def calculate_aspect_ratio(height, root_chord_length, tip_chord_length):
            
            area = ((root_chord_length + tip_chord_length) / 2 ) * height
            return height**2 / area
        
        def calculate_taper_ratio(tip_chord, root_chord):
            return tip_chord / root_chord

        


        epsilon = calculate_epsilon(tip_chord_length, root_chord_length, sweep_length)
        DN = calculate_denominator_constant(epsilon, p_0)
        aspect_ratio = calculate_aspect_ratio(height, root_chord_length, tip_chord_length)
        taper_ratio = calculate_taper_ratio(tip_chord_length, root_chord_length)

        return speed_of_sound * np.sqrt((shear_modulus) / ((DN * aspect_ratio**3)/((fin_thickness / root_chord_length)**3 * (aspect_ratio + 2)) * (taper_ratio + 1)/(2) * (air_pressure)/(p_0)))

    @staticmethod
    def calculate_temperature_at_altitude(h):
        return 288.16 - (0.0065 * h)

    @staticmethod
    def calculate_speed_of_sound(T):
        '''
        Calculate the speed of sound (v) based on the temperature (T) in Kelvin.
        v = sqrt(gamma * R * T)
        Assume: gamma = 1.4 for air, R = 287 J/kg k

        Parameters:
        T: Temperate in Kelvin

        Returns:
        Speed of sound in m/s
        '''
        gamma = 1.4
        R = 287.0

        return np.sqrt(gamma * R * T)

    @staticmethod
    def calculate_temperature_at_altitude(h):
        return 288.16 - (0.0065 * h)

    @staticmethod
    def calculate_air_pressure(T):  
        return 101.325e3 * ((T)/(288.16))**5.256
    
    @staticmethod
    def plot_flutter_velocity_at_altitude(results):
        altitudes = results["altitude"]
        flutter_velocities = results["flutter_velocity"]
        safe_velocities = results["safe_velocity"]



        plt.title("Flutter Velocity vs. Altitude")
        plt.xlabel("Altitude (m)")
        plt.ylabel("Flutter Velocity (m/s)")

        plt.xlim([min(altitudes), max(altitudes)])
        plt.ylim([0, 100 * round((max(flutter_velocities) + 50 )/100)])

        plt.grid(visible=True, which='both')
        plt.minorticks_on()
        plt.plot(altitudes, flutter_velocities, linestyle='solid', color='blue', label='Flutter Velocity')

        plt.plot(altitudes, safe_velocities, linestyle='dashed', color='red', label='Max Safe Velocity')

        plt.legend()
        plt.show()


        
