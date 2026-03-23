# src/core/solver.py

import math

import numpy as np
from scipy.integrate import solve_ivp

from .config_system import conv_coeff, H, dz

def _edge_rate(du_dt, u, dx, dy, T_amb, cool_surface, rho_mat, heat_cap_mat):
    # cooling only over the thin edge/rim; Completly isolated top and bottom, no heat transfer
    # same mechanism as with cool_surface=True
    # edge_x means the edge parallel to the x axis; origin=lower
    const_edge_x_high = conv_coeff / (rho_mat[-1, :] * dy * heat_cap_mat[-1, :])
    const_edge_x_low = conv_coeff / (rho_mat[0, :] * dy * heat_cap_mat[0, :])
    const_edge_y_left = conv_coeff / (rho_mat[:, 0] * dx * heat_cap_mat[:, 0])
    const_edge_y_right = conv_coeff / (rho_mat[:, -1] * dx * heat_cap_mat[:, -1])
    
    # if is_vectorized=True a new axis is needed (same as in _heat_equation)
    if u.ndim == 3:
        const_edge_x_high = const_edge_x_high[:, np.newaxis]
        const_edge_x_low = const_edge_x_low[:, np.newaxis]
        const_edge_y_left = const_edge_y_left[:, np.newaxis]
        const_edge_y_right = const_edge_y_right[:, np.newaxis]
    
    du_dt[0, ...] -= const_edge_x_low * (u[0, ...] - T_amb)
    du_dt[-1, ...] -= const_edge_x_high * (u[-1, ...] - T_amb)
    du_dt[:, 0, ...] -= const_edge_y_left * (u[:, 0, ...] - T_amb)
    du_dt[:, -1, ...] -= const_edge_y_right * (u[:, -1, ...] - T_amb)
       
    if cool_surface:
        const_surface = (2 * conv_coeff) / (rho_mat * H * dz * heat_cap_mat)
        if u.ndim == 3:
            const_surface = const_surface[:, :, np.newaxis]
        # implement newtonian cooling (convection) but neglecting radiational losses (stefan boltzmann law) due to computational cost (T^4 dependency)
        # Newton's law of cooling : q = h * (T - T_amb) --> edge_temp_rate = const * (T - T_amb)
        # q = heat flux [W/m^2]; h = heat transfer coefficient [W/(m^2 * K)]
        # since q is linearly proportional to edge_temp_rate they only differ by a const. --> h --> const
        # precisely const = (2 (top and bottom site of the sheet) * convection_coeff (~ 10 for slight convection) / (rho * heat_cap * thickness))
        cooling_rate = const_surface * (u - T_amb)
        du_dt -= cooling_rate
        
    return du_dt



def _heat_equation(t, u0_flat, N, M, lambda_mat, rho_mat, heat_cap_mat, q_mat, dx, dy, T_amb, cool_surface):
    # for vectorisation
    k = u0_flat.shape[1] if u0_flat.ndim > 1 else 1
    if k == 1:
        u = u0_flat.reshape(N, M)
        pad_width = 1
        is_vectorized = False
    else:
        u = u0_flat.reshape(N, M, -1)
        pad_width = ((1, 1), (1, 1), (0, 0))
        is_vectorized = True
    
    # Ghost Cells: creates adiabatic boundary conditions
    u_padded = np.pad(u, pad_width=pad_width, mode='edge') 
    lambda_padded = np.pad(lambda_mat, pad_width=1, mode='edge')

    if is_vectorized:
        rho_mat_calc = rho_mat[..., np.newaxis]
        heat_cap_mat_calc = heat_cap_mat[..., np.newaxis]
        q_mat_calc = q_mat[..., np.newaxis]
        lambda_padded_calc = lambda_padded[..., np.newaxis]
    else:
        rho_mat_calc = rho_mat
        heat_cap_mat_calc = heat_cap_mat
        q_mat_calc = q_mat
        lambda_padded_calc = lambda_padded

    gradient_part_x = ( ( (2*lambda_padded_calc[1:-1, 2:]*lambda_padded_calc[1:-1, 1:-1]) / (lambda_padded_calc[1:-1, 2:] + lambda_padded_calc[1:-1, 1:-1]) )
                        * (u_padded[1:-1, 2:] - u_padded[1:-1, 1:-1])
                        - ( (2*lambda_padded_calc[1:-1, 1:-1]*lambda_padded_calc[1:-1, :-2]) / (lambda_padded_calc[1:-1, 1:-1] + lambda_padded_calc[1:-1, :-2]) )
                        * (u_padded[1:-1, 1:-1] - u_padded[1:-1, :-2])) / dx**2
    
    gradient_part_y = ( ( (2*lambda_padded_calc[2:, 1:-1]*lambda_padded_calc[1:-1, 1:-1]) / (lambda_padded_calc[2:, 1:-1] + lambda_padded_calc[1:-1, 1:-1]) )
                        * (u_padded[2:, 1:-1] - u_padded[1:-1, 1:-1])
                        - ( (2*lambda_padded_calc[:-2, 1:-1]*lambda_padded_calc[1:-1, 1:-1]) / (lambda_padded_calc[:-2, 1:-1] + lambda_padded_calc[1:-1, 1:-1]) )
                        * (u_padded[1:-1, 1:-1] - u_padded[:-2, 1:-1])) / dy**2

    du_dt = 1/(rho_mat_calc * heat_cap_mat_calc) * (q_mat_calc + gradient_part_x + gradient_part_y)
        
    
    # edge temperature change handling (with and without convection cooling on top and bottom)
    du_dt = _edge_rate(du_dt, u, dx, dy, T_amb, cool_surface, rho_mat, heat_cap_mat)    
    
    return du_dt.reshape(u0_flat.shape)
    


def HeatEquationSolver(lambda_mat, q_mat, u0, t_span, N, M, dx, dy, T_amb, rho_mat, heat_cap_mat, cool_surface=True):
    # --- Solve heat equation --- 
    u0_flat = u0.flatten()
    print("Start integration...")
    sol = solve_ivp(_heat_equation,
                    t_span=t_span,
                    y0=u0_flat,
                    method="BDF",               # industry standard for stiff differential equations
                    args=(N, M, lambda_mat, rho_mat, heat_cap_mat, q_mat, dx, dy, T_amb, cool_surface),
                    vectorized=True)  
    print("Integration completed.")                            # end progress bar
    num_of_timesteps = sol.y.shape[1]           # number of time steps for which the equation is solved
    sol_T = sol.y.T                             # transposes from (length of flattened matrix, timesteps) --> (timesteps, length of flattened matrix)
    final_sol = sol_T.reshape((num_of_timesteps, N, M))
    sol_time = sol.t
    return sol_time, final_sol
