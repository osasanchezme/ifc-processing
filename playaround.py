# https://wiki.osarch.org/index.php?title=IfcOpenShell_code_examples

import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element

ifc = ifcopenshell.open('../Example2_TrueCoords.ifc')

# print(ifc.schema) # What is the schema of the file

# print(ifc.by_id(1)) # Get the Organization (origin software)

# print(ifc.by_guid('124A5FBdX3d9FYqYfR6P$r')) # Get the line correspondig to that element
# my_elem = ifc.by_guid('124A5FBdX3d9FYqYfR6P$r') # Get the line correspondig to that element
# info = ['0-GlobalID:', '1-Owner history:', '2-Name:Tag:', '3-None:', '4-Name:', '5-Local placement:', '6-ProductDefinitionShape:', '7-Tag:']
# for i in range(len(my_elem)):
#     print(f"{info[i]} {my_elem[i]}")
# print(type(ifc.by_guid('124A5FBdX3d9FYqYfR6P$r'))) # And its class

beams = ifc.by_type('IfcBeam')
print(f"The model has {len(beams)} beams.") # Get the number of beams
beam = beams[0] # Get the first beam
# print(beam.id()) # Get the STEP ID. The # line in the ifc file where the element is written
print(beam.Name) # The same as beam[2]
# print(beam.GlobalId) # The same as beam[0]
# print(beam.get_info()) # Get a dictionary with all the info of the element

# print(ifcopenshell.util.element.get_psets(beam)) # Get all the properties and quantities associated with the element

# print(beam.IsDefinedBy) # Get inverse attributes, those that reference that elements

# print(ifc.get_inverse(beam)) # Get all the elements referencing this element. All the other lines referencing this element

# print(ifc.traverse(beam)) # Get all the elements, our element is referencing. Meaning all the lines

