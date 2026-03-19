# src/core/config_system.py

import numpy as np

# set thicknes for heat rate claculation (dz = scale, H = number of layers)
H = 2
dz = 0.001

def initialise_matrices(N, M, components, heat_sources, initial_heat_spots, boundary_conditions):
    # Initialise alpha matrix
    alpha = np.zeros(shape=(N,M))
    alpha[:, :] = 2.3e-5                # "substrate" made of iron
    for component in components:
        alpha[component.bottom_left[1] : component.top_right[1], component.bottom_left[0] : component.top_right[0]] = component.alpha

    # Initialise temperature rate matrix (for heating)
    temp_rate_mat = np.zeros_like(alpha)
    for temp_rate_src in heat_sources:
        temp_rate_mat[temp_rate_src.bottom_left[1] : temp_rate_src.top_right[1], temp_rate_src.bottom_left[0] : temp_rate_src.top_right[0]] = temp_rate_src.temp_rate

    # Initialise initial heat map
    u0 = np.zeros_like(alpha)
    u0[:, :] = 23
    for heat_spot in initial_heat_spots:
        u0[heat_spot.bottom_left[1] : heat_spot.top_right[1], heat_spot.bottom_left[0] : heat_spot.top_right[0]] = heat_spot.temp

    u0[0, :] = boundary_conditions.get("top")
    u0[-1, :] = boundary_conditions.get("bottom")
    u0[:, 0] = boundary_conditions.get("left")
    u0[:, -1] = boundary_conditions.get("right")
    
    return alpha, temp_rate_mat, u0
