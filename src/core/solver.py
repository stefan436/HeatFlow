# src/core/solver.py

import math

import numpy as np
from scipy.integrate import solve_ivp

from .config_system import conv_coeff, H, dz
from .material import material_db

def _edge_rate(du_dt, u, alpha, dx, dy, T_amb, cool_surface):
        # fetch density and heat capacity of substrate material (the material with alpha [0; 0])
    for properties in material_db.values():
        alpha_look_up, rho, heat_cap = properties
        if math.isclose(alpha_look_up, alpha[0, 0], rel_tol=1e-9):
            break

    # cooling const (assuming no components at the edge)
    const = conv_coeff / (rho * H * dz * heat_cap)
       
            
    if cool_surface:
        const = const * 2
        # boundary conditions with Ellipsis (...) operator works for 2D und 3D
        # since the edge of the matrix is not taken into account in the calculation above, we copy the neighboring value to the edge
        du_dt[0, ...] = du_dt[1, ...]        
        du_dt[-1, ...] = du_dt[-2, ...]
        du_dt[:, 0, ...] = du_dt[:, 1, ...]
        du_dt[:, -1, ...] = du_dt[:, -2, ...]
        
        # implement newtonian cooling (convection) but neglecting radiational losses (stefan boltzmann law) due to computational cost (T^4 dependency)
        # Newton's law of cooling : q = h * (T - T_amb) --> edge_temp_rate = const * (T - T_amb)
        # q = heat flux [W/m^2]; h = heat transfer coefficient [W/(m^2 * K)]
        # since q is linearly proportional to edge_temp_rate they only differ by a const. --> h --> const
        # precisely const = (2 (top and bottom site of the sheet) * convection_coeff (~ 10 for slight convection) / (rho * heat_cap * thickness))
        cooling_rate = const * (u - T_amb)
        du_dt -= cooling_rate
    
    else:
        # cooling only over the thin edge/rim; Completly isolated top and bottom, no heat transfer
        # same mechanism as with cool_surface=True
        
        du_dt[0, :] = alpha[0, :] * (u[1, :] - u[0, :]) / dy**2 + const * (T_amb - u[0, :])
        du_dt[-1, :] = alpha[-1, :] * (u[-2, :] - u[-1, :]) / dy**2 + const * (T_amb - u[-1, :])
        du_dt[:, 0] = alpha[:, 0] * (u[:, 1] - u[:, 0]) / dx**2 + const * (T_amb - u[:, 0])
        du_dt[:, -1] = alpha[:, -1] * (u[:, -2] - u[:, -1]) / dx**2 + const * (T_amb - u[:, -1])
        
    return du_dt



def _heat_equation(t, u0_flat, N, M, alpha, temp_rate_mat, dx, dy, T_amb, cool_surface):
    # for vectorisation
    k = u0_flat.shape[1] if u0_flat.ndim > 1 else 1
    if k == 1:
        u = u0_flat.reshape(N, M)
        is_vectorized = False
    else:
        u = u0_flat.reshape(N, M, -1)
        is_vectorized = True
    
    du_dt = np.zeros_like(u)

    a = alpha[1:-1, 1:-1]
    temp_rate = temp_rate_mat[1:-1, 1:-1]

    if is_vectorized:
        a = alpha[1:-1, 1:-1, np.newaxis]
        temp_rate = temp_rate_mat[1:-1, 1:-1, np.newaxis]
    
    du_dt[1:-1, 1:-1] = a * ((u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[0:-2, 1:-1]) / dx**2 +
                             (u[1:-1, 2:] - 2*u[1:-1, 1:-1] + u[1:-1, 0:-2]) / dy**2) + temp_rate
    
    
    # edge temperature change handling (with and without convection cooling on top and bottom)
    du_dt = _edge_rate(du_dt, u, alpha, dx, dy, T_amb, cool_surface)    
    
    return du_dt.reshape(u0_flat.shape)    # returns the vector of the derivatives in the same shape as the input u0_flat
                                # solve_ivp only understands 1D (2D if vectorized) inputs, thus, flatten/reshape
    


def HeatEquationSolver(alpha, temp_rate_mat, u0, t_span, N, M, dx, dy, T_amb, cool_surface=True):
    # --- Solve heat equation --- 
    u0_flat = u0.flatten()
    print("Start integration...")
    sol = solve_ivp(_heat_equation,
                    t_span=t_span,
                    y0=u0_flat,
                    method="LSODA",
                    args=(N, M, alpha, temp_rate_mat, dx, dy, T_amb, cool_surface),
                    vectorized=True)  # Radau solver better for stiff problems 
    print("Integration completed.")                            # end progress bar
    num_of_timesteps = sol.y.shape[1]           # number of time steps for which the equation is solved
    sol_T = sol.y.T                             # transposes from (length of flattened matrix, timesteps) --> (timesteps, length of flattened matrix)
    final_sol = sol_T.reshape((num_of_timesteps, N, M))
    return final_sol
