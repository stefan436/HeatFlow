# src/core/initialise_shapes.py

import numpy as np

from .component_shapes import Circle
from .material import fetch_material_properties
from .config_system import H, dz

def initialise_matrices(N, M, substrate_material, components, heat_sources, initial_heat_spots, T_amb, dx, dy):
    substr_lambda, substr_rho , substr_heat_cap = fetch_material_properties(substrate_material)
    
    # Initialise lambda_mat matrix
    lambda_mat = np.zeros(shape=(N,M))
    lambda_mat[:, :] = substr_lambda
    # Initialise auxiliary matrix (rho and heat cap)
    rho_mat = np.zeros_like(lambda_mat)
    heat_cap_mat = np.zeros_like(lambda_mat)
    rho_mat[:, :] = substr_rho
    heat_cap_mat[:, :] = substr_heat_cap
    for component in components:
        
        if isinstance(component, Circle):
            lambda_mat[component.circular_mask] = component.lambda_val
            rho_mat[component.circular_mask] = component.rho
            heat_cap_mat[component.circular_mask] = component.heat_cap
        else:
            lambda_mat[component.bottom_left[1] : component.top_right[1], component.bottom_left[0] : component.top_right[0]] = component.lambda_val
            rho_mat[component.bottom_left[1] : component.top_right[1], component.bottom_left[0] : component.top_right[0]] = component.rho
            heat_cap_mat[component.bottom_left[1] : component.top_right[1], component.bottom_left[0] : component.top_right[0]] = component.heat_cap

    # Initialise heat flow rate matrix (for heating)
    q_mat = np.zeros_like(lambda_mat)
    for heat_source in heat_sources:
        if isinstance(heat_source, Circle):
            q_mat[heat_source.circular_mask] = heat_source.power / (H * dz)
        else:
            q_mat[heat_source.bottom_left[1] : heat_source.top_right[1],
                  heat_source.bottom_left[0] : heat_source.top_right[0]] = heat_source.power / (H * dz)            
    
    # Initialise initial heat map
    u0 = np.zeros_like(lambda_mat)
    u0[:, :] = T_amb
    for heat_spot in initial_heat_spots:
        
        if isinstance(heat_spot, Circle):
            u0[heat_spot.circular_mask] = heat_spot.temp
        else:
            u0[heat_spot.bottom_left[1] : heat_spot.top_right[1], heat_spot.bottom_left[0] : heat_spot.top_right[0]] = heat_spot.temp
    
    return lambda_mat, q_mat, u0, rho_mat, heat_cap_mat
