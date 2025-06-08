# Martin's method for flutter esimtation https://www.apogeerockets.com/education/downloads/Newsletter615.pdf

import numpy as np


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

def calculate_temperature_at_altitude(h):
    return 288.16 - (0.0065 * h)

def calculate_air_pressure(T):

    return 101.325e3 * ((T)/(288.16))**5.256


def calculate_flutter_velocity(speed_of_sound, shear_modulus, aspect_ratio, fin_thickness, root_chord_length, taper_ratio, air_pressure, sweep_length, tip_chord_length):
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
    


    epsilon = calculate_epsilon(tip_chord_length, root_chord_length, sweep_length)
    DN = calculate_denominator_constant(epsilon, p_0)

    return speed_of_sound * np.sqrt((shear_modulus) / ((DN * aspect_ratio**3)/((fin_thickness / root_chord_length)**3 * (aspect_ratio + 2)) * (taper_ratio + 1)/(2) * (air_pressure)/(p_0)))



h = 18500*0.3048

shear_modulus = 600000 *6894.76
aspect_ratio = 0.6
fin_thickness = 0.125 * 0.0254 
root_chord_length = 7.5 * 0.0254
taper_ratio = 0.33333
sweep_length = 4.285 * 0.0254
tip_chord_length = 2.5 * 0.0254

# Calculate temperature from altitude
T = calculate_temperature_at_altitude(h)
print(f"Temperature: {T} K, {(T - 273.15) * 9/5 + 32} F")


# Calculate speed of sound from temperature
speed_of_sound = calculate_speed_of_sound(T)
print(f"Speed of sound: {speed_of_sound} m/s, {speed_of_sound * 3.28084} ft/s")

# Calculate air pressure from temperature
air_pressure = calculate_air_pressure(T)
print(f"Air pressure: {air_pressure} Pa, {air_pressure * 0.000145038} psi")

# Calculate flutter velocity
flutter_velocity = calculate_flutter_velocity(speed_of_sound, shear_modulus, aspect_ratio, fin_thickness, root_chord_length, taper_ratio, air_pressure, sweep_length, tip_chord_length)
print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
print(f"Flutter velocity: {flutter_velocity} m/s, {flutter_velocity * 3.28084} ft/s")




