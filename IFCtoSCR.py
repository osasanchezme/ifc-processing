### Coded by: Oscar Sanchez. osasanchezme@unal.edu.co

import ifcopenshell
from ifcopenshell import geom


def read_geom(ifc_path, ObjType):
    """Function to read elements from a ifc file

    Args:
        ifc_path (str): Full or relative path of the ifc file
        ObjType (str): IfcType of the elements want to get back

    Returns:
        dict: Dictionary containing the vertices, edges and face of each element, using the globally unique id
    """
    ifc_file = ifcopenshell.open(ifc_path)
    settings = geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    ios_vertices = {}
    ios_edges = {}
    ios_faces = {}
    ios_elements = {}

    for ifc_entity in ifc_file.by_type(ObjType): # Retrieves all the elements of the given type
        # print(ifc_entity[8]) # From 0 up to 8
        # print(ifc_entity) # Gives the ifc file line of the element
        # print(ifc_entity[0]) # Gives the globally unique universal id of the element
        # print(ifc_entity[7]) # Gives the tag/Revit ID of the element
        shape = geom.create_shape(settings, ifc_entity) # Convert the ifc into a mesh
        # ios stands for IfcOpenShell
        ios_vertices[ifc_entity[0]] = shape.geometry.verts
        ios_edges[ifc_entity[0]] = shape.geometry.edges
        ios_faces[ifc_entity[0]] = shape.geometry.faces
        ios_elements[ifc_entity[0]] = ifc_entity[7]

    return {"vertices": ios_vertices, "edges": ios_edges, "faces": ios_faces, "elements": ios_elements}

def writePoints(vertices, file_name):
    """Function to write the points into a scr file

    Args:
        vertices (list): list containing a tuple with (x,y,z) coords for each vertex
        file_name (str): name of the file to be written with the autocad points
    """
    with open(file_name, "w") as f:
        f.write("zoom -100,-100,-100 -200,-200,-200\n")
        for point in vertices:
            p_str = str(point).replace(" ", "")
            p_str = f"point {p_str}\n"
            p_str = p_str.replace("(", "")
            p_str = p_str.replace(")", "")
            f.write(p_str)
        f.write("zoom a\n")
        f.close()
    print(f"Successfully exported the points to: {file_name}")

def writeLines(lines, file_name, mode = "w"):
    """Function to write the lines into a scr file

    Args:
        lines (list): list containing a tuple with ((xi, yi, zi), (xj, yj, zj)) for each line
        file_name (str): name of the file to be written with the autocad lines
    """
    with open(file_name, mode) as f:
        f.write("zoom -100,-100,-100 -200,-200,-200\n")
        for point in lines:
            p_str = str(point).replace(" ", "")
            p_str = f"line {p_str} \n"
            p_str = p_str.replace("),(", " ")
            p_str = p_str.replace("(", "")
            p_str = p_str.replace(")", "")
            f.write(p_str)
        f.write("zoom a\n")
        f.close()
    print(f"Successfully exported the lines to: {file_name}")

def idealizeBeam(elementLines):
    """Generates the idealized line for the given element (beam), top-middle line in the longest direction.

    Args:
        elementLines (list): List containing all the lines ((xi,yi,zi), (xj,yj,zj)) that define the element's geometry
    Returns:
        tuple: Tuple containing coords ((xi,yi,zi),(xj,yj,zj)) of the idealized beam
    """
    def calcLength(line):
        line_length = ((line[0][0]-line[1][0])**2 + (line[0][1]-line[1][1])**2 + (line[0][2]-line[1][2])**2)**0.5
        return line_length

    def calcMidPoint(line):
        x_mid = (line[0][0] + line[1][0])/2
        y_mid = (line[0][1] + line[1][1])/2
        z_mid = (line[0][2] + line[1][2])/2
        return (x_mid, y_mid, z_mid)

    zs = []
    topLines = []
    for line in elementLines:
        zs.append(line[0][2])
        zs.append(line[1][2])
    z_max = max(zs)
    for line in elementLines:
        if line[0][2] == z_max and line[1][2] == z_max:
            topLines.append(line)
    idealBeam = ((0., 0., 0.), (0., 0., 0.))
    for i in range(len(topLines)):
        init_point = calcMidPoint(topLines[i])
        for j in range(i,len(topLines)):
            end_point = calcMidPoint(topLines[j])
            candidate = (init_point, end_point)
            if calcLength(candidate) > calcLength(idealBeam):
                idealBeam = candidate
    return idealBeam

def idealizeColumn(elementLines):
    def calcAvgPoint(lines):
        x_avg, y_avg, z_avg = 0,0,0
        for line in lines:
            x_avg += line[0][0] + line[1][0]
            y_avg += line[0][1] + line[1][1]
            z_avg += line[0][2] + line[1][2]
        x_avg /= len(lines)*2
        y_avg /= len(lines)*2
        z_avg /= len(lines)*2
        print(len(lines))
        return (x_avg, y_avg, z_avg)
    zs = []
    interestingLines = []
    topLines = []
    bottomLines = []
    for line in elementLines:
        if line[0][2] == line[1][2]:
            interestingLines.append(line)
            if line[0][2] in zs:
                pass
            else:
                zs.append(line[0][2])

    for line in interestingLines:
        if line[0][2] == max(zs):
            topLines.append(line)
        else:
            bottomLines.append(line)
    return (calcAvgPoint(bottomLines), calcAvgPoint(topLines))

def process_beams_columns(input_ifc_file_path, element_type, output_elem_filename, output_ideal_filename):
    ifc_values = read_geom(input_ifc_file_path, element_type)
    vertices, edges, faces, elements = ifc_values['vertices'], ifc_values['edges'], ifc_values['faces'], ifc_values['elements']
    f = open(output_elem_filename, "w")
    f.close()
    f = open(output_ideal_filename, "w")
    f.close()
    for key in elements: # Loop through the keys of each element
        print(f"\n\n----------------Element with UUID: {key} and tag: {elements[key]}----------------")
        # Preprocessing
        points = [ vertices[key][i*3:i*3+3] for i in range(len(vertices[key])//3) ]
        line_points = [ edges[key][i*2:i*2+2] for i in range(len(edges[key])//2) ] #List containing a tuple for each line with start and end points id
        line_points = list(set(line_points)) # The line vertices pointers are duplicated, delete duplicates
        lines = [ (points[line_points[i][0]], points[line_points[i][1]]) for i in range(len(line_points)) ] # List of tuples containing the xyz coords of the start and end point
        # writeLines(lines, f"Line_{key}.scr") # To write lines for a single element - Don't use

        # Exporting
        # writeLines(lines, elementsFile, "a") # To write lines for all the elements
        if element_type=="IfcBeam":
            writeLines(lines, output_elem_filename, "a")
            idealBeam = [idealizeBeam(lines)] # Pass an element as an argument and gives back a line
            writeLines(idealBeam, output_ideal_filename, "a")
        elif element_type=="IfcColumn":
            writeLines(lines, output_elem_filename, "a")
            idealColumn = [idealizeColumn(lines)]
            writeLines(idealColumn, output_ideal_filename, "a")

if __name__ == "__main__":
    process_beams_columns("../Example2.ifc", "IfcBeam", "3dBeams.scr","IdealBeams.scr")
    process_beams_columns("../Example2.ifc", "IfcColumn", "3dColumns.scr","IdealColumns.scr")
