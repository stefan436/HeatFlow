# src/core/config_system.py

import numpy as np

def initialise_matrices(N, M, components, heat_sources, initial_heat_spots, boundary_conditions):
    # Initialise alpha matrix
    alpha = np.zeros(shape=(N,M))
    alpha[:, :] = 2.3e-5                # "substrate" made of iron
    for component in components:
        alpha[component.bottom_left[1] : component.top_right[1], component.bottom_left[0] : component.top_right[0]] = component.alpha

    # Initialise heat source matrix
    Q = np.zeros_like(alpha)
    for q_source in heat_sources:
        Q[q_source.bottom_left[1] : q_source.top_right[1], q_source.bottom_left[0] : q_source.top_right[0]] = q_source.temp

    # Initialise initial heat map
    u0 = np.zeros_like(alpha)
    u0[:, :] = 23
    for heat_spot in initial_heat_spots:
        u0[heat_spot.bottom_left[1] : heat_spot.top_right[1], heat_spot.bottom_left[0] : heat_spot.top_right[0]] = heat_spot.temp

    u0[0, :] = boundary_conditions.get("top")
    u0[-1, :] = boundary_conditions.get("bottom")
    u0[:, 0] = boundary_conditions.get("left")
    u0[:, -1] = boundary_conditions.get("right")
    
    return alpha, Q, u0
