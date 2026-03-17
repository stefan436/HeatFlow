# src/core/solver.py

import numpy as np
from scipy.integrate import solve_ivp

from .config_system import *

def _heat_equation(t, u0_flat):
    u = u0_flat.reshape(N,M)
    
    du_dt = np.zeros_like(u)

    # boundary conditions
    du_dt[0, :] = 0        
    du_dt[-1, :] = 0       
    du_dt[:, 0] = 0
    du_dt[:, -1] = 0
    
    # vector slicing: if [1:-1] is taken from a numpy array we get the original array without the first and the last entry
    # the next line calculates the whole array at once (this is vectorisation)
    
    du_dt[1:-1, 1:-1] = alpha * ((u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[0:-2, 1:-1]) / dx**2 +
                                 (u[1:-1, 2:] - 2*u[1:-1, 1:-1] + u[1:-1, 0:-2]) / dy**2)
    
    return du_dt.flatten()    # returns the vector of the derivatives
                                # solve_ivp only understands 1D inputs, thus, flatten
    


def HeatEquationSolver(u0):
    u0_flat = u0.flatten()
    sol = solve_ivp(_heat_equation, t_span=t_span, y0=u0_flat)
    num_of_timesteps = sol.y.shape[1]           # number of time steps for which the equation is solved
    sol_T = sol.y.T                             # transposes from (length of flattened matrix, timesteps) --> (timesteps, length of flattened matrix)
    final_sol = sol_T.reshape((num_of_timesteps, N, M))
    return final_sol



