# src/core/component_shapes.py

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
        # self.top_left     = (self.x_center - self.half_side_length, self.y_center + self.half_side_length)
        # self.bottom_right = (self.x_center + self.half_side_length, self.y_center - self.half_side_length)
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
        
        # if self.x_center + self.half_side_length < M or self.x_center - self.half_side_length < 0:
        #     raise ValueError("Square has to be within the Matrix N x M.")
        # if self.y_center + self.half_side_length < N or self.y_center - self.half_side_length < 0:
        #     raise ValueError("Square has to be within the Matrix N x M.")
        

        
        
    def __repr__(self):                 # if print(Square) is called, this function is executed
        return f"Square(Center: {self.x_center}/{self.y_center}, Side: {self.side_length})"