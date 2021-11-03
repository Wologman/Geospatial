# Use a csv list with one file name item per row in column [0], to open geotifs into a single raster

from qgis.utils import iface
import ntpath, sys, os, importlib, time, shutil, processing
from pathlib import Path   # This is the modern way to handle the / vs \ difference between Windows & Linux
from qgis.core import *
from qgis import processing
import gdal
from csv import reader

# To make this work, run it from anywhere, but check the relative location of the source files
# with respect to the project directory.  (which is relative to the CWD)
# Store the list as a csv of the file names or at least the unique bit.  
# Adjust the path variables below as needed

# Careful!!!!!
# Attribute table:  CC11_1000_0839
# Actual file name: DEM_CC11_2016_1000_0839.tif   The 2016_1000 is common to all!
# Use: prefix + 1st + middle + 2nd + suffix  'DEM_' + [CC11] + '_2016_1000_' + 0839 + '.tif'

source_folder = 'Source/source_tiles' # relative to the directory containing the project file
prefix = 'DEM_'
middle = '_2016_1000_'
suffix = '.tif'
working_folder = Path('Scratch')
scratch = Path('Scratch')
results = Path('Results')
tile_list_path = str(working_folder / 'selected_tiles.csv')

parent = iface.mainWindow()

if not QgsProject.instance().fileName():
    print('No project is loaded yet')
    prj_fn, prjOK = QFileDialog.getOpenFileNames(parent, "Open a project file", 
                QgsProject.instance().homePath(),"Project Files (*.qgz)")
    if prjOK:
        QMessageBox.information(parent, "Success", "Opening {}...".format(prj_fn))
        print('Loaded: ', prj_fn[0])
        QgsProject.instance().read(prj_fn[0])
    else:
        QMessageBox.warning(parent, "Warning", "No project file selected, the process needs a project to work")
else:
    print('Project filepath:', QgsProject.instance().fileName())

prjpath = Path(QgsProject.instance().fileName()).parent #set the pjpath to the folder with the project file

os.chdir(prjpath)  # Makes the current working directory match the location of python files
sys.path.append(os.getcwd())  # only needed to call other scripts from this one.
print('Current working directory: ', os.getcwd())

#make a list
tile_list = []
with open(tile_list_path, 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        # row variable is a list that represents a row in csv
        first, last = row[0][0:4], row[0][-4:]
        tile_filename = prefix + first + middle + last + suffix
        tile_list.append(str(prjpath / source_folder / tile_filename))

#use this to turn a list of tiffs into the mosaic using a virtual layer
vrt_out = str(prjpath / scratch / 'vrt.vrt')  


build_vrt_prm = {'INPUT': tile_list,
    'RESOLUTION':1,
    'SEPARATE':False,
    'PROJ_DIFFERENCE':False,
    'ADD_ALPHA':False,
    'ASSIGN_CRS':None,
    'RESAMPLING':0,
    'SRC_NODATA':'',
    'OUTPUT': vrt_out}  #Could put this in memory instead? it's small.

processing.run('gdal:buildvirtualraster', build_vrt_prm)

mosaic_path = str(results / 'merged.tif')
translate_prm = {'INPUT': vrt_out, 'FORMAT' : 'GTiff', 'OUTPUT': mosaic_path}
processing.run('gdal:translate', translate_prm)

# Load the mosaic
rlayer = QgsRasterLayer(mosaic_path, "LiDAR DEM")

if not rlayer.isValid():
    print("Layer failed to load!")

iface.addRasterLayer(mosaic_path, 'LiDAR DEM')

'''
# Just testing the idea for a single file.
tif_name = Path(source_file_prefix + 'CB11_2016_1000_4123' + source_file_suffix)
tif_path = str(source_folder_name / tiff_name)
print(tiff_path)
rlayer = QgsRasterLayer(tif_path, "layer name")

if not rlayer.isValid():
    print("Layer failed to load!")
iface.addRasterLayer(tif_path)
'''