from finsolver.config import FinConfig
import numpy as np
from numpy import trapz
from scipy.linalg import eig
from scipy.special import kv as besselk
from pprint import pprint

def theodorsen(k):
    val = besselk(1, 1j * k) / (besselk(0, 1j * k) + besselk(1, 1j * k))
    print(f"[DEBUG] Theodorsen({k:.3f}) = {val}")
    return val

def calculate_flutter(config: FinConfig) -> str:
    print("[DEBUG] Full FinConfig Input:")
    pprint(config.to_dict())
    
    layers = [config.core] + config.layers
    print(f"[DEBUG] Number of layers including core: {len(layers)}")
    for i, layer in enumerate(layers):
        print(f"[DEBUG] Layer {i}: material={layer.material}, E={layer.E}, G={layer.G}, thickness={layer.thickness}, "
              f"root_chord={layer.root_chord}, tip_chord={layer.tip_chord}, height={layer.height}, density={layer.density}")

    L = sum(layer.height for layer in layers) / len(layers)
    print(f"[DEBUG] Calculated span L = {L:.6f} m")

    avg_chord = 0.5 * (config.core.root_chord + config.core.tip_chord)
    print(f"[DEBUG] Core root chord = {config.core.root_chord}, tip chord = {config.core.tip_chord}")
    print(f"[DEBUG] Average chord (core) = {avg_chord:.6f} m")

    b = avg_chord / 2
    a = 0.25  # elastic axis location as fraction of chord
    print(f"[DEBUG] Semi-chord (b) = {b:.6f} m, Elastic axis (a) = {a:.2f}")

    rho_air = 1.225  # Air density
    print(f"[DEBUG] Air density rho_air = {rho_air} kg/m³")

    # Mass per unit span m̄
    mbar_layers = [layer.density * layer.thickness for layer in layers]
    print(f"[DEBUG] Layer mass/thickness contributions: {mbar_layers}")
    mbar = sum(mbar_layers) * avg_chord
    print(f"[DEBUG] Calculated mass per unit span m̄ = {mbar:.6f} kg/m")

    Iwing = mbar * b**2
    print(f"[DEBUG] Calculated mass moment of inertia Iwing = {Iwing:.6e} kg·m²/m")

    EI_layers = [layer.E * (layer.thickness ** 3) / 12 for layer in layers]
    print(f"[DEBUG] Layer bending stiffness contributions EI: {EI_layers}")
    EI = sum(EI_layers)
    print(f"[DEBUG] Total bending stiffness EI = {EI:.6e} Nm²")

    GJ_layers = [layer.G * avg_chord * (layer.thickness ** 3) / 3 for layer in layers]
    print(f"[DEBUG] Layer torsional stiffness contributions GJ: {GJ_layers}")
    GJ = sum(GJ_layers)
    print(f"[DEBUG] Total torsional stiffness GJ = {GJ:.6e} Nm²")

    NP = 100
    y_L = np.linspace(0, 1, NP + 1)
    print(f"[DEBUG] y_L shape: {y_L.shape}")

    N, M = 2, 2
    print(f"[DEBUG] Using N={N} bending modes, M={M} torsional modes")

    Del = np.zeros((N, N))
    Bmat = np.zeros((N, N))
    Cmat = np.zeros((N, M))
    Dmat = np.zeros((M, M))
    Tmat = np.zeros((M, M))

    for i in range(N):
        psi_i = y_L ** (i + 1)
        psi_i_dd = ((i + 1) * (i)) * y_L ** (i - 1) / L**2 if i > 0 else np.zeros_like(y_L)
        for j in range(N):
            psi_j = y_L ** (j + 1)
            psi_j_dd = ((j + 1) * (j)) * y_L ** (j - 1) / L**2 if j > 0 else np.zeros_like(y_L)
            Del[i, j] = trapz(psi_i * psi_j, y_L)
            Bmat[i, j] = trapz(psi_i_dd * psi_j_dd, y_L)

    print(f"[DEBUG] Del matrix:\n{Del}")
    print(f"[DEBUG] Bmat matrix:\n{Bmat}")

    for i in range(M):
        phi_i = y_L ** i
        phi_i_d = (i) * y_L ** (i - 1) / L if i > 0 else np.zeros_like(y_L)
        for j in range(M):
            phi_j = y_L ** j
            phi_j_d = (j) * y_L ** (j - 1) / L if j > 0 else np.zeros_like(y_L)
            Dmat[i, j] = trapz(phi_i * phi_j, y_L)
            Tmat[i, j] = trapz(phi_i_d * phi_j_d, y_L)

    print(f"[DEBUG] Dmat matrix:\n{Dmat}")
    print(f"[DEBUG] Tmat matrix:\n{Tmat}")

    for i in range(N):
        psi_i = y_L ** (i + 1)
        for j in range(M):
            phi_j = y_L ** j
            Cmat[i, j] = trapz(psi_i * phi_j, y_L)

    print(f"[DEBUG] Cmat matrix:\n{Cmat}")

    Mwing = np.block([
        [mbar * Del, -mbar * a * b * Cmat],
        [-mbar * a * b * Cmat.T, Iwing * Dmat]
    ])
    K = np.block([
        [EI * Bmat, np.zeros((N, M))],
        [np.zeros((M, N)), GJ * Tmat]
    ])

    print(f"[DEBUG] Mwing matrix:\n{Mwing}")
    print(f"[DEBUG] K matrix:\n{K}")

    k_vals = np.arange(0.01, 10, 0.01)
    U_flutter = None
    mode_flutter = None

    for k in k_vals:
        Ck = theodorsen(k)
        A_mat = 2 * np.pi * b * k**2 * np.block([
            [Del, a * b * Cmat],
            [a * b * Cmat.T, b**2 * (a**2 + 1 / 8) * Dmat]
        ])
        B_mat = -2 * np.pi * k * 1j * np.block([
            [2 * Ck * Del, -b * (1 + 2 * (0.5 - a) * Ck) * Cmat],
            [2 * b * (0.5 + a) * Ck * Cmat.T, b**2 * (0.5 - a) * (1 - 2 * (0.5 + a) * Ck) * Dmat]
        ])
        C_mat = -2 * np.pi * b * np.block([
            [np.zeros_like(Cmat), -2 * Ck * Cmat],
            [np.zeros_like(Cmat.T), -b * (1 + 2 * a) * Ck * Dmat]
        ])

        A_hat = A_mat + B_mat + C_mat
        try:
            eigvals = eig(K, Mwing + 0.5 * rho_air * b**2 / k**2 * A_hat)[0]
        except Exception as e:
            print(f"[ERROR] Eigenvalue computation failed at k={k:.2f}: {e}")
            continue

        eigvals_real = np.real(eigvals)
        eigvals_real[eigvals_real <= 0] = np.nan
        omega = np.sqrt(1.0 / eigvals_real)
        damping = -0.5 * np.imag(eigvals)

        print(f"[DEBUG] k={k:.2f}, omega={omega}, damping={damping}")

        for i, d in enumerate(damping):
            if d > 1e-4 and not np.isnan(omega[i]):
                U_flutter = omega[i] * b / k
                mode_flutter = i + 1
                print(f"[DEBUG] Flutter detected at k={k:.2f}: U={U_flutter:.2f} m/s, Mode={mode_flutter}")
                break
        if U_flutter:
            break

    result = "Flutter Analysis Results:\n\n"

    if U_flutter is not None:
        result += f"Estimated Flutter Speed: {U_flutter:.2f} m/s (Mode {mode_flutter})\n"
    else:
        result += "Estimated Flutter Speed: Not found (no unstable mode detected in range).\n"

    result += f"Bending Modes Used: {N}, Torsional Modes Used: {M}\n"
    result += f"Semi-chord (b): {b:.4f} m, Elastic Axis (a): {a:.2f}\n"
    result += f"Wing Span (L): {L:.4f} m\n"
    result += f"Torsional Stiffness (GJ): {GJ:.2e} Nm²\n"
    result += f"Bending Stiffness (EI): {EI:.2e} Nm²\n"
    result += f"Mass/Unit Span (m̄): {mbar:.4f} kg/m\n"
    result += f"Mass Moment of Inertia: {Iwing:.4e} kg·m²/m\n"

    return result
