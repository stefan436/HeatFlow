# src/core/material.py

import json

with open("src/data/properties.json", mode="r", encoding="utf-8") as properties_file:
    data = json.load(properties_file)
    material_db = {
        entry["material"]: [entry["thermal_conductivity_W_m_K"], entry["density_kg_m3"], entry["specific_heat_capacity_J_kg_K"]] 
        for entry in data 
        if "material" in entry
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
        
    th_cond, rho, heat_cap = properties
    
    return th_cond, rho, heat_cap
