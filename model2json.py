def create_json(floor_heights, floor_nodes, idealBeamsDict, idealColumnsDict):
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

    print(f"Nodes:\n{nodes}")
    print(f"Columns:\n{columns}")
    print(f"Beams:\n{beams}")