# main.py

import matplotlib.pyplot as plt

from code.solver import HeatEquationSolver
from code.config_system import u0
from code.visualisation import *

if __name__ == "__main__":
    sol_tensor = HeatEquationSolver(u0)
    
    print("Initial State")
    initial_state(sol_tensor)
    show_until_enter()
        
    print("Final State")
    final_state(sol_tensor)
    show_until_enter()
    
    print("Slider Animation")
    interactive_heat_map(sol_tensor)
    plt.show()
    
    print("Animation")
    animate_heat(sol_tensor)
    plt.show()