# main.py

import matplotlib.pyplot as plt

from core.solver import HeatEquationSolver
from core.config_system import initialise_matrices
from core.visualisation import *
from core.material import display_available_materials
from core.component_shapes import *


# ============================
# User Input
# ============================

# values are for the colorbars
temp_min = 20
temp_max = 50

# size of the plate in mm (scale is determined by dx and dy)
# origin is bottom left
N = 100
M = 100

# 1mm distance (defines scale)
dx = 0.001
dy = 0.001

# time span over which is integrated (seconds)
t_span = (1, 180)  

# Components which are placed on iron substrate
components = [
    Square(x_center=25, y_center=25, side_length=10, material="Copper at 25 °C"),
    Square(x_center=75, y_center=75, side_length=10, material="Copper at 25 °C")
]

# permanent heating power density (in W/m^2)
heat_sources = [
    Square(x_center=25, y_center=25, side_length=9, material="Copper at 25 °C", power=1000000),
    Square(x_center=75, y_center=75, side_length=9, material="Copper at 25 °C", power=1000000)
]

# Initial heat map (rest is at room temp/23)
initial_heat_spots = [
    Square(x_center=50, y_center=50, side_length=5, temp=23)
]

# permanent boundary conditions (choose room temp; infinite cooling power)
boundary_condition = {"bottom": 23, 
                      "right": 23,
                      "top": 23,
                      "left": 23}


# ============================
# user Input End
# ============================




if __name__ == "__main__":
    display_available_materials()    
    
    alpha, temp_rate_mat, u0 = initialise_matrices(N, M,
                                       components,
                                       heat_sources,
                                       initial_heat_spots,
                                       boundary_condition)
    
    print("Setup Dashboard")
    plot_setup_dashboard(alpha, temp_rate_mat, u0)
    show_until_enter()
    
    sol_tensor = HeatEquationSolver(alpha, temp_rate_mat, u0, t_span, N, M, dx, dy)
    
    print("Initial State")
    initial_state(sol_tensor, temp_min, temp_max, alpha=alpha) 
    show_until_enter()
        
    print("Final State")
    final_state(sol_tensor, temp_min, temp_max, alpha=alpha)
    show_until_enter()
    
    # print("Slider Animation")
    # interactive_heat_map(sol_tensor)
    # plt.show()
    
    print("Animation")
    ani = animate_heat(sol_tensor, temp_min, temp_max, alpha=alpha)
    plt.show()