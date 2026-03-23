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

# size of the plate in mm (scale is determined by dx and dy)
# origin is bottom left
M = 100         # x direction
N = 100         # y direction

# 1mm distance (defines scale)
dx = 0.001
dy = 0.001

# time span over which is integrated (seconds)
t_span = (1, 3600)

# Choose substrate Material
substrate_material = "Beton"


# Components which are placed on iron substrate
# First component in list is "lowest" layer, last component is "top" layer and replaces "lower" layers (if they overlap). 
# component must pass material
components = [
    Rectangle(x_center=50, y_center=50, x_length=4, y_length=50, material="Bitumen"),
    Square(x_center=50, y_center=25, side_length=10, material="Eisen"),
    Square(x_center=50, y_center=75, side_length=10, material="Eisen")
]

# permanent heating power density (in W/m^2)
# Same hierarchy as with components 
# heat_source must pass power
heat_sources = [
    Circle(N, M, x_center=50, y_center=25, radius=20, power=1000000),
    Circle(N, M, x_center=50, y_center=75, radius=20, power=1000000)
]

# Initial heat map (rest is at room temp/t_amb)
# Same hierarchy as with components 
# initial_heat_spots must pass temp
initial_heat_spots = [
    Square(x_center=50, y_center=50, side_length=5, temp=100)
]


# Choose ambient temperature 
T_amb = 23

# Cool over top and bottom surface (or only thin edges)? defaults to True
cool_surface = False

# ============================
# user Input End
# ============================




if __name__ == "__main__":
    display_available_materials()    
    
    lambda_mat, q_mat, u0, rho_mat, heat_cap_mat = initialise_matrices(N, M,
                                                                          substrate_material,
                                                                          components,
                                                                          heat_sources,
                                                                          initial_heat_spots, 
                                                                          T_amb,
                                                                          dx, dy)
    
    print("Setup Dashboard")
    plot_setup_dashboard(lambda_mat, q_mat, u0)
    show_until_enter()
    
    time_steps, sol_tensor = HeatEquationSolver(lambda_mat, q_mat, u0, t_span, N, M, dx, dy, T_amb, rho_mat, heat_cap_mat, cool_surface)
    temp_min, temp_max = sol_tensor.min(), sol_tensor.max()
    
    print("Initial State")
    initial_state(sol_tensor, temp_min, temp_max, lambda_mat=lambda_mat) 
    show_until_enter()
        
    print("Final State")
    final_state(sol_tensor, temp_min, temp_max, lambda_mat=lambda_mat)
    show_until_enter()

    print("Animation")
    fig_ani, ani = animate_heat(time_steps, sol_tensor, temp_min, temp_max, lambda_mat=lambda_mat)
    show_until_enter()
    
    print("Slider Animation")
    fig_slider, slider = interactive_heat_map(time_steps, sol_tensor, temp_min, temp_max, lambda_mat=lambda_mat)
    show_until_enter()