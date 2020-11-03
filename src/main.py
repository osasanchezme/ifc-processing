### Coded by: Oscar Sanchez. osasanchezme@unal.edu.co

from model2json import create_json
from ifc2scr import process_file

if __name__ == "__main__":
    floor_heights, floor_nodes, idealBeamsDict, idealColumnsDict, beamNamesDict, columnNamesDict = process_file("5_Floors_RectangularBeams.ifc", "3dModel.scr","IdealModel.scr", export_scr=True)
    create_json(floor_heights, floor_nodes, idealBeamsDict, idealColumnsDict, beamNamesDict, columnNamesDict, "5_Floors_RectangularBeams.json")