import re
import json

def create_json(floor_heights, floor_nodes, idealBeamsDict, idealColumnsDict, beamNamesDict, columnNamesDict, jsonFile):
    """Takes floor_nodes, ideal beams and ideal columns to generate a JSON file

    Args:
        floor_nodes (dict): A dictionary containing the coords for each node in every floor (key)
        idealBeamsDict (dict): A dictionary with UUID and Tag for each beam element as key and its coords as values
        idealColumnsDict (dict): A dictionary with UUID and Tag for each column element as key and its coords as values
    """

    # Get a dictionary with level names Nnumber, starting from 0
    floor_heights.sort()
    levels = {}
    N = 0
    for level in floor_heights:
        levels[str(level)] = "N" + str(N)
        N += 1

    # Get level heights tags from revit in the ifc file
    # Speed up things by deleting unused variables

    # Get a dictionary numbering nodes by level
    nodes = {}
    for key in floor_nodes:
        i = 1
        for node in floor_nodes[key]:
            str_key = levels[key] + "-" + str(i)
            i += 1
            nodes[str_key] = node
    
    # Refactor idealColumns and idealBeams by using named nodes - IMPROVE BY ONLY LOOKING IN THE SAME FLOOR - CHECK IF ALL NODES WERE FOUND
    beams = {}
    columns = {}

    for beam in idealBeamsDict:
        start_node = idealBeamsDict[beam][0][0]
        end_node = idealBeamsDict[beam][0][1]
        found = 0
        for node in nodes:
            if found == 1: break # Speeding up line

            if start_node == nodes[node]:
                start_node = node
                found += 0.5
            elif end_node == nodes[node]:
                end_node = node
                found += 0.5
        beams[beam] = (start_node, end_node)

    for column in idealColumnsDict:
        start_node = idealColumnsDict[column][0][0]
        end_node = idealColumnsDict[column][0][1]
        found = 0
        for node in nodes:
            if found == 1: break # Speeding up line

            if start_node == nodes[node]:
                start_node = node
                found += 0.5
            elif end_node == nodes[node]:
                end_node = node
                found += 0.5
        columns[column] = (start_node, end_node)

    # Get all the rectangular sections in the model
    beam_rectangular_sections = {}
    column_rectangular_sections = {}
    beams_section = {}
    columns_section = {}
    beams_tag = {}
    columns_tag = {}

    for name in beamNamesDict:
        abstraction = re.search(r"([\w -]*):([0-9]*) x ([0-9]*)(\w*):([0-9]*)",beamNamesDict[name])
        if re.search(r".*Concrete.*Rect.*Beam",abstraction.group(1)):
            key = 'CRB-' + abstraction.group(2) + 'x' + abstraction.group(3) + abstraction.group(4)
            beam_rectangular_sections[key] = (abstraction.group(2), abstraction.group(3))
            beams_section[name] = key
            beams_tag[name] = abstraction.group(5)
            # Add a try catch to be faster

    for name in columnNamesDict:
        abstraction = re.search(r"([\w -]*):([0-9]*) x ([0-9]*)(\w*):([0-9]*)",columnNamesDict[name])
        if re.search(r".*Concrete.*Rect.*Column",abstraction.group(1)):
            key = 'CRC-' + abstraction.group(2) + 'x' + abstraction.group(3) + abstraction.group(4)
            column_rectangular_sections[key] = (abstraction.group(2), abstraction.group(3))
            columns_section[name] = key
            columns_tag[name] = abstraction.group(5)

    # FEM.js like JSON exporting

    myJSON = {}

    myJSON["materials"] = {"Concrete":{"E":20.636e9, "G":7.692e9}} # In N / m2, E = 3900*sqrt(f'c) G = E / (2*(1+v))
    myJSON["sections"] = {}
    myJSON["joints"] = {}
    myJSON["frames"] = {}
    myJSON["supports"] = {}

    # Sections in meters
    conversion_factors = {
        'mm': 1/1000,
        'cm': 1/100,
        'inch': 0.0254,
        'ft': 0.3048,
        'm': 1.0,
    }
    for section in beam_rectangular_sections:
        name = section
        units = re.search(r".*[0-9]*x[0-9]*(\w*)", name).group(1)
        width = float(beam_rectangular_sections[section][0]) * conversion_factors[units]
        height = float(beam_rectangular_sections[section][1]) * conversion_factors[units]
        a = max([width, height])/2
        b = min([width, height])/2
        myJSON["sections"][name] = {
            "area" : width * height,
            "Ix" : a * b**3 * (16/3 - 3.36*(b/a)*(1-(b**4/(12*a**4)))),# J
            "Iy" : width**3 * height / 12,
            "Iz" : width * height**3 / 12,
            "type" : "RectangularSection",
            "width" : width,
            "height" : height,
        }

    for section in column_rectangular_sections:
        name = section
        units = re.search(r".*[0-9]*x[0-9]*(\w*)", name).group(1)
        width = float(column_rectangular_sections[section][0]) * conversion_factors[units]
        height = float(column_rectangular_sections[section][1]) * conversion_factors[units]
        a = max([width, height])/2
        b = min([width, height])/2
        myJSON["sections"][name] = {
            "area" : width * height,
            "Ix" : a * b**3 * (16/3 - 3.36*(b/a)*(1-(b**4/(12*a**4)))),# J
            "Iy" : width**3 * height / 12,
            "Iz" : width * height**3 / 12,
            "type" : "RectangularSection",
            "width" : width,
            "height" : height,
        }
    for node in nodes:
        myJSON["joints"][node] = {
            "x" : nodes[node][0],
            "y" : nodes[node][1],
            "z" : nodes[node][2],
        }
        if 'N0' in node:
            myJSON["supports"][node] = {
                "ux": "true",
                "uy": "true",
                "uz": "true",
                "rx": "true",
                "ry": "true",
                "rz": "true"
            }

    for beam in beams:
        myJSON["frames"][beams_tag[beam]] = {
            "j" : beams[beam][0],
            "k" : beams[beam][1],
            "material" : "Concrete", # Assigned by brute force
            "section" : beams_section[beam],
        }
    
    for column in columns:
        myJSON["frames"][columns_tag[column]] = {
            "j" : columns[column][0],
            "k" : columns[column][1],
            "material" : "Concrete", # Assigned by brute force
            "section" : columns_section[column],
        }

    with open(jsonFile, "w") as file:
        json.dump(myJSON, file)
        print(f"Successfully exported the file to {jsonFile}")

    # print(myJSON)
    # print(f"Nodes:\n{nodes}")
    # print(f"Beam rectangular sections:\n{beam_rectangular_sections}")
    # print(f"Column rectangular sections:\n{beam_rectangular_sections}")
    
    # print(f"Columns' nodes:\n{columns}")
    # print(f"\n\nColumns' section:\n{columns_section}")
    # print(f"\n\nColumns' tag:\n{columns_tag}")
    # print(f"\n\nBeams' nodes:\n{beams}")
    # print(f"\n\nBeams' section:\n{beams_section}")
    # print(f"\n\nBeams' tag:\n{beams_tag}")
    

    # Watch the units problem
