# main.py

import matplotlib.pyplot as plt

from core.solver import HeatEquationSolver
from core.visualisation import *
from core.material import display_available_materials
from core.component_shapes import *
from core.initialise_shapes import initialise_matrices


# ============================
# User Input
# ============================

# values are for the colorbars
temp_min = 20
temp_max = 50

# size of the plate in mm (scale is determined by dx and dy)
# origin is bottom left
M = 100         # x direction
N = 100         # y direction

# 1mm distance (defines scale)
dx = 0.001
dy = 0.001

# time span over which is integrated (seconds)
t_span = (1, 60)


# Components which are placed on iron substrate
# First component in list is "lowest" layer, last component is "top" layer and replaces "lower" layers (if they overlap). 
components = [
    Rectangle(x_center=50, y_center=50, x_length=4, y_length=50, material="Copper at 25 °C"),
    Square(x_center=50, y_center=25, side_length=10, material="Silicon"),
    Square(x_center=50, y_center=75, side_length=10, material="Silicon")
]

# permanent heating power density (in W/m^2)
# Same hierarchy as with components 
heat_sources = [
    Circle(N, M, x_center=50, y_center=25, radius=5, material="Silicon", power=1000000),
    Circle(N, M, x_center=50, y_center=75, radius=5, material="Silicon", power=1000000)
]

# Initial heat map (rest is at room temp/23)
# Same hierarchy as with components 
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