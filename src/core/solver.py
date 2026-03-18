# src/core/solver.py

import numpy as np
from scipy.integrate import solve_ivp
from tqdm import tqdm

from .config_system import *

def _heat_equation(t, u0_flat):
    k = u0_flat.shape[1] if u0_flat.ndim > 1 else 1
    if k == 1:
        u = u0_flat.reshape(N, M)
        is_vectorized = False
    else:
        u = u0_flat.reshape(N, M, -1)       # -1 is an ambiguous number in numpy language
        is_vectorized = True
    
    du_dt = np.zeros_like(u)

    # boundary conditions with Ellipsis (...) operator works for 2D und 3D
    # info about Ellipsis operator: to address all dimensions following the first two, regardless of whether there are none, one or many
    du_dt[0, ...] = 0        
    du_dt[-1, ...] = 0       
    du_dt[:, 0, ...] = 0
    du_dt[:, -1, ...] = 0

    a = alpha[1:-1, 1:-1]
    q = Q[1:-1, 1:-1]

    if is_vectorized:
        a = alpha[1:-1, 1:-1, np.newaxis]
        q = Q[1:-1, 1:-1, np.newaxis]
    
    # vector slicing: if [1:-1] is taken from a numpy array we get the original array without the first and the last entry
    # the next line calculates the whole array at once (this is vectorisation)
    # numpy broadcasting takes care of the dimensionality in u; only a new dimension/axis has to be added to a and q
    
    du_dt[1:-1, 1:-1] = a * ((u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[0:-2, 1:-1]) / dx**2 +
                             (u[1:-1, 2:] - 2*u[1:-1, 1:-1] + u[1:-1, 0:-2]) / dy**2) + q
    
    return du_dt.reshape(u0_flat.shape)    # returns the vector of the derivatives in the same shape as the input u0_flat
                                # solve_ivp only understands 1D (2D if vectorized) inputs, thus, flatten/reshape
    


def HeatEquationSolver(u0):
    # --- Solve heat equation --- 
    u0_flat = u0.flatten()
    print("Start integration...")
    sol = solve_ivp(_heat_equation,
                    t_span=t_span,
                    y0=u0_flat,
                    method="RK45",
                    vectorized=True)  # Radau solver better for stiff problems 
    print("Integration completed.")                            # end progress bar
    num_of_timesteps = sol.y.shape[1]           # number of time steps for which the equation is solved
    sol_T = sol.y.T                             # transposes from (length of flattened matrix, timesteps) --> (timesteps, length of flattened matrix)
    final_sol = sol_T.reshape((num_of_timesteps, N, M))
    return final_sol



