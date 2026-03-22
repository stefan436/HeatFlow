# src/core/initialise_shapes.py

import numpy as np

from .component_shapes import Circle
from .material import fetch_material_properties, fetch_material_props_from_alpha
from .config_system import dz, H

def initialise_matrices(N, M, substrate_material, components, heat_sources, initial_heat_spots, T_amb):
    substr_alpha, _ , _ = fetch_material_properties(substrate_material)
    
    # Initialise alpha_mat matrix
    alpha_mat = np.zeros(shape=(N,M))
    alpha_mat[:, :] = substr_alpha
    for component in components:
        
        if isinstance(component, Circle):
            alpha_mat[component.circular_mask] = component.alpha
        else:
            alpha_mat[component.bottom_left[1] : component.top_right[1], component.bottom_left[0] : component.top_right[0]] = component.alpha


    # Initialise auxiliary matrix (rho and heat cap)
    unique_alphas, unique_alphas_idx = np.unique(alpha_mat, return_inverse=True)
    unique_rho, unique_heat_cap = np.array([]), np.array([])
    for idx, val in enumerate(unique_alphas):
        material_properties = fetch_material_props_from_alpha(alpha=val)
        unique_rho, unique_heat_cap = np.append(unique_rho, material_properties[1]), np.append(unique_heat_cap, material_properties[2])
        
    rho_mat = unique_rho[unique_alphas_idx]
    heat_cap_mat = unique_heat_cap[unique_alphas_idx]
    

    # Initialise temperature rate matrix (for heating)
    temp_rate_mat_final = np.zeros_like(alpha_mat)
    for temp_rate_src in heat_sources:
        # calculate temp rate for given heat source using rho_mat and heat_cap_mat
        temp_rate_mat = (temp_rate_src.power) / (rho_mat * dz * H * heat_cap_mat)  # Formula based on: heating power [W/m^2] * area = m * heat_cap [J/(K * kg)] * temp_rate [K/S] = rho * area * thickness (dz*H) * heat_cap * temp_rate
        if isinstance(temp_rate_src, Circle):
            temp_rate_mat_final[temp_rate_src.circular_mask] = temp_rate_mat[temp_rate_src.circular_mask]
        else:
            temp_rate_mat_final[temp_rate_src.bottom_left[1] : temp_rate_src.top_right[1],
                                temp_rate_src.bottom_left[0] : temp_rate_src.top_right[0]] = temp_rate_mat[temp_rate_src.bottom_left[1] : temp_rate_src.top_right[1],
                                                                                                           temp_rate_src.bottom_left[0] : temp_rate_src.top_right[0]]

    # Initialise initial heat map
    u0 = np.zeros_like(alpha_mat)
    u0[:, :] = T_amb
    for heat_spot in initial_heat_spots:
        
        if isinstance(heat_spot, Circle):
            u0[heat_spot.circular_mask] = heat_spot.temp
        else:
            u0[heat_spot.bottom_left[1] : heat_spot.top_right[1], heat_spot.bottom_left[0] : heat_spot.top_right[0]] = heat_spot.temp
    
    return alpha_mat, temp_rate_mat_final, u0
