# src/core/component_shapes.py

import numpy as np

from .material import fetch_material_properties
from .config_system import dz, H

class Square():
    def __init__(self, x_center, y_center, side_length, material=None, temp=None, power=None):
        self.material = material
        self.temp = temp
        self.power = power
        self.x_center = x_center
        self.y_center = y_center
        self.side_length = side_length
        
        
        # geometric implementation of the component
        self.half_side_length = self.side_length // 2
        
        self.bottom_left  = (self.x_center - self.half_side_length, self.y_center - self.half_side_length)
        self.top_right    = (self.x_center + self.half_side_length, self.y_center + self.half_side_length)
        
        
        # fetch material properties for heat source and component properties
        if material is not None:
            self.alpha, self.rho, self.heat_cap = fetch_material_properties(self.material)
        elif temp is None:                      # material is not needed if the a heat map initiallised. In this case, temp is mandatory
            raise ValueError(f"\nError: Square at Position X:{self.x_center}/Y:{self.y_center} "
                             f"Material is missing!\n")
        
        # calculate temp rate for given heat source
        if power is not None:
            if material is None:
                raise ValueError(f"\nError: Heat Source at Position X:{self.x_center}/Y:{self.y_center} "
                                 f"has power (={self.power}), but no material!\n")
            self.temp_rate = (self.power) / (self.rho * dz * H * self.heat_cap)             # Formula based on: heating power [W/m^2] * area = m * heat_cap [J/(K * kg)] * temp_rate [K/S] = rho * area * thickness (dz*H) * heat_cap * temp_rate
        
    def __repr__(self):                 # if print(Square) is called, this function is executed
        return f"Square (Center: {self.x_center}/{self.y_center}, Side: {self.side_length})"
    
    
class Rectangle():
    def __init__(self, x_center, y_center, x_length, y_length, material=None, temp=None, power=None):
        self.material = material
        self.temp = temp
        self.power = power
        self.x_center = x_center
        self.y_center = y_center
        self.x_length = x_length
        self.y_length = y_length
        
        
        # geometric implementation of the component
        self.half_x_length = self.x_length // 2
        self.half_y_length = self.y_length // 2
        
        self.bottom_left  = (self.x_center - self.half_x_length, self.y_center - self.half_y_length)
        self.top_right    = (self.x_center + self.half_x_length, self.y_center + self.half_y_length)
        
        
        # fetch material properties for heat source and component properties
        if material is not None:
            self.alpha, self.rho, self.heat_cap = fetch_material_properties(self.material)
        elif temp is None:                      # material is not needed if the a heat map initiallised. In this case, temp is mandatory
            raise ValueError(f"\nError: Square at Position X:{self.x_center}/Y:{self.y_center} "
                             f"Material is missing!\n")
        
        # calculate temp rate for given heat source
        if power is not None:
            if material is None:
                raise ValueError(f"\nError: Heat Source at Position X:{self.x_center}/Y:{self.y_center} "
                                 f"has power (={self.power}), but no material!\n")
            self.temp_rate = (self.power) / (self.rho * dz * H * self.heat_cap)             # Formula based on: heating power [W/m^2] * area = m * heat_cap [J/(K * kg)] * temp_rate [K/S] = rho * area * thickness (dz*H) * heat_cap * temp_rate
        
    def __repr__(self):                 # if print(Square) is called, this function is executed
        return f"Rectangele (Center: {self.x_center}/{self.y_center}, Sides: {self.x_length}/{self.y_length})"
    
    
class Circle():
    def __init__(self, N, M, x_center, y_center, radius, material=None, temp=None, power=None):
        self.material = material
        self.temp = temp
        self.power = power
        self.x_center = x_center
        self.y_center = y_center
        self.radius = radius
        
        
        # geometric implementation of the component
        Y, X = np.ogrid[:N, :M]
        
        dist_from_center = ( (X - x_center)**2 + (Y - y_center)**2 )**(1/2)
        
        self.circular_mask = dist_from_center < self.radius

        # fetch material properties for heat source and component properties
        if material is not None:
            self.alpha, self.rho, self.heat_cap = fetch_material_properties(self.material)
        elif temp is None:                      # material is not needed if the a heat map initiallised. In this case, temp is mandatory
            raise ValueError(f"\nError: Square at Position X:{self.x_center}/Y:{self.y_center} "
                             f"Material is missing!\n")
        
        # calculate temp rate for given heat source
        if power is not None:
            if material is None:
                raise ValueError(f"\nError: Heat Source at Position X:{self.x_center}/Y:{self.y_center} "
                                 f"has power (={self.power}), but no material!\n")
            self.temp_rate = (self.power) / (self.rho * dz * H * self.heat_cap)             # Formula based on: heating power [W/m^2] * area = m * heat_cap [J/(K * kg)] * temp_rate [K/S] = rho * area * thickness (dz*H) * heat_cap * temp_rate
        
    def __repr__(self):                 # if print(Square) is called, this function is executed
        return f"Circle (Center: {self.x_center}/{self.y_center}, Radius: {self.radius})"