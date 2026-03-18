# src/core/component_shapes.py

from .material import fetch_material_properties

class Square():
    def __init__(self, x_center, y_center, side_length, material=None, temp=None):
        self.material = material
        self.temp = temp
        self.x_center = x_center
        self.y_center = y_center
        self.side_length = side_length
        self.alpha = fetch_material_properties(self.material)
        
        self.half_side_length = self.side_length // 2
        
        # if self.x_center + self.half_side_length < M or self.x_center - self.half_side_length < 0:
        #     raise ValueError("Square has to be within the Matrix N x M.")
        # if self.y_center + self.half_side_length < N or self.y_center - self.half_side_length < 0:
        #     raise ValueError("Square has to be within the Matrix N x M.")
        
        
        self.bottom_left  = (self.x_center - self.half_side_length, self.y_center - self.half_side_length)
        # self.top_left     = (self.x_center - self.half_side_length, self.y_center + self.half_side_length)
        # self.bottom_right = (self.x_center + self.half_side_length, self.y_center - self.half_side_length)
        self.top_right    = (self.x_center + self.half_side_length, self.y_center + self.half_side_length)
        
    def __repr__(self):                 # if print(Square) is called, this function is executed
        return f"Square(Center: {self.x_center}/{self.y_center}, Side: {self.side_length})"