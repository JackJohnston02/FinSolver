from finsolver.models.homogenisation import Homogenisation
from finsolver.models.martins_method import FlutterAnalysisMartinsMethod




def run_flutter_analysis(config):

    
    homogeniser = Homogenisation()
    equivalent_fin = homogeniser.calculate_equivalent_fin(config)

    flutter_solver = FlutterAnalysisMartinsMethod()

    flutter_results = flutter_solver.analyse_fin(equivalent_fin)
    



    return  str({
        "root_chord_length (m)": equivalent_fin.root_chord,
        "tip_chord_length (m)": equivalent_fin.tip_chord,
        "height (m)": equivalent_fin.height,
        "sweep_length (m)": equivalent_fin.sweep_length,
        "shear_modulus (Pa)": equivalent_fin.shear_modulus,
        "total_thickness (m)": equivalent_fin.thickness
        })
    ...
