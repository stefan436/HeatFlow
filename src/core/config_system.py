# src/core/config_system.py

import numpy as np

N = 100
M = 100

dx = 0.1
dy = 0.1
alpha = 1

# time span over which is integrated
t_span = (1, 10)  

# boundary conditions
bc_top = 0.0     
bc_bottom = 0.0   
bc_left = 0.0   
bc_right = 0.0    

# initial conditions
u0 = np.zeros(shape=(N,M))
u0[40:60, 40:60] = 100     # middle of the rod is at 100 °C

u0[0, :] = bc_top
u0[-1, :] = bc_bottom
u0[:, 0] = bc_left
u0[:, -1] = bc_right

vmin = 0
vmax = 100