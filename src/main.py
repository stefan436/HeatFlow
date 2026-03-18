# main.py

import matplotlib.pyplot as plt

from core.solver import HeatEquationSolver
from core.config_system import u0
from core.visualisation import *

if __name__ == "__main__":
    sol_tensor = HeatEquationSolver(u0)
    
    print("Initial State")
    initial_state(sol_tensor)
    show_until_enter()
        
    print("Final State")
    final_state(sol_tensor)
    show_until_enter()
    
    # print("Slider Animation")
    # interactive_heat_map(sol_tensor)
    # plt.show()
    
    print("Animation")
    animate_heat(sol_tensor)
    plt.show()