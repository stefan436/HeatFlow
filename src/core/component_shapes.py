# src/core/component_shapes.py

import numpy as np

from .material import fetch_material_properties


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
        
        
        # check validity of the input
        inputs = [material, temp, power]
        # count number of not None
        if sum(v is not None for v in inputs) == 1:
            if material is not None:
                self.lambda_val, self.rho, self.heat_cap = fetch_material_properties(self.material)
            elif temp is not None:
                pass
            else:
                pass
        else:
            raise ValueError("Exactly one of the three parameters (material, temp, power) must be specified")

        
    def __repr__(self):
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
        
        
        # check validity of the input
        inputs = [material, temp, power]
        # count number of not None
        if sum(v is not None for v in inputs) == 1:
            if material is not None:
                self.lambda_val, self.rho, self.heat_cap = fetch_material_properties(self.material)
            elif temp is not None:
                pass
            else:
                pass
        else:
            raise ValueError("Exactly one of the three parameters (material, temp, power) must be specified")
        
    def __repr__(self):
        return f"Rectangle (Center: {self.x_center}/{self.y_center}, Sides: {self.x_length}/{self.y_length})"
    
    
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

        # check validity of the input
        inputs = [material, temp, power]
        # count number of not None
        if sum(v is not None for v in inputs) == 1:
            if material is not None:
                self.lambda_val, self.rho, self.heat_cap = fetch_material_properties(self.material)
            elif temp is not None:
                pass
            else:
                pass
        else:
            raise ValueError("Exactly one of the three parameters (material, temp, power) must be specified")
        
    def __repr__(self):
        return f"Circle (Center: {self.x_center}/{self.y_center}, Radius: {self.radius})"