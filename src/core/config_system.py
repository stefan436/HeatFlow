# src/core/config_system.py

from turtle import shape

import numpy as np

vmin = 0
vmax = 100

# 10cm plate
N = 100
M = 100

# 1mm distance
dx = 0.001
dy = 0.001

# alpha for Al
alpha_val = 9.7e-5
alpha = np.zeros(shape=(N,M))
alpha[:, :] = alpha_val

# time span over which is integrated (seconds)
t_span = (1, 60)  

# boundary conditions
bc_top = 0.0     
bc_bottom = 0.0   
bc_left = 0.0   
bc_right = 0.0    

# initial conditions
u0 = np.zeros_like(alpha)
u0[40:60, 40:60] = 100     # middle of the rod is at 100 °C

u0[0, :] = bc_top
u0[-1, :] = bc_bottom
u0[:, 0] = bc_left
u0[:, -1] = bc_right

# heat source 
Q = np.zeros_like(alpha)
Q[40:60, 40:60] = 100 