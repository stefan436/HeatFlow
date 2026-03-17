# src/settings.py

import numpy as np

N = 100
M = 100

dx = 0.1
dy = 0.2
alpha = 1

t_span = (1, 10)  # time span over which is integrated

# example input
u0 = np.zeros(shape=(N,M))
u0[40:60, 40:60] = 100     # middle of the rod is at 100 °C

vmin = 0
vmax = 100