# src/core/material.py

import json

with open("src/data/properties.json", mode="r", encoding="utf-8") as properties_file:
    data = json.load(properties_file)
    material_db = {
        entry["material"]: [entry["diffusivity_mm2_s"] / 1e6, entry["density_kg_m3"], entry["specific_heat_capacity_J_kg_K"]] # /1e6 converts into SI units (from mm^2/s to m^2/s)
        for entry in data 
        if "material" in entry                              # adds only entrys where material is available
    }
    
    
def display_available_materials():
    print(f"Verfügbare Materialien sind: {list(material_db.keys())}")
    
    
def fetch_material_properties(material_name):
    """Fetches material properties from the properties.json"""
    if material_name == None:
        return None
    
    properties = material_db.get(material_name)
    if properties is None:
        raise ValueError(f"Material '{material_name}' wurde in der properties.json nicht gefunden! "
                         f"Verfügbar sind: {list(material_db.keys())}")
        
    alpha, rho, heat_cap = properties
    
    return alpha, rho, heat_cap
