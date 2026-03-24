# src/core/material.py

import json
from collections import defaultdict

material_db = {}
category_db = defaultdict(list) # Speichert { "Kategorie": ["Mat1", "Mat2", ...] }

with open("src/data/properties.json", mode="r", encoding="utf-8") as properties_file:
    data = json.load(properties_file)
    for entry in data:
        if "material" in entry:
            mat_name = entry["material"]
            # "Sonstige if category is not found"
            cat_name = entry.get("category", "Sonstige") 
            
            material_db[mat_name] = [
                entry["thermal_conductivity_W_m_K"], 
                entry["density_kg_m3"], 
                entry["specific_heat_capacity_J_kg_K"]
            ]
            category_db[cat_name].append(mat_name)

# sort alphabetically
for cat in category_db:
    category_db[cat].sort()

sorted_categories = sorted(category_db.keys())

def get_category_for_material(material_name):
    """Findet die Kategorie für ein gegebenes Material (wichtig für den Edit-Dialog)."""
    for cat, mats in category_db.items():
        if material_name in mats:
            return cat
    return "Sonstige"


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
