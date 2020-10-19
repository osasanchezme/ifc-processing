import re

def create_json(floor_heights, floor_nodes, idealBeamsDict, idealColumnsDict, beamNamesDict, columnNamesDict):
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

    print(f"Nodes:\n{nodes}")
    print(f"Beam rectangular sections:\n{beam_rectangular_sections}")
    print(f"Column rectangular sections:\n{beam_rectangular_sections}")
    
    print(f"Columns' nodes:\n{columns}")
    print(f"Columns' section:\n{columns_section}")
    print(f"Columns' tag:\n{columns_tag}")
    print(f"Beams' nodes:\n{beams}")
    print(f"Beams' section:\n{beams_section}")
    print(f"Beams' tag:\n{beams_tag}")
    

    # Watch the units problem
