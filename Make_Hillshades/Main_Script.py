# To work, this script, plus any modules need to go in the same directory as the QGIS project file
from qgis.utils import iface
import ntpath, sys, os, importlib
from qgis.core import *
import Find_DEM as find_dem
import DEM_Style as dem_style
import processing

importlib.reload(dem_style)  # Only needed while editing the module to make it re-load after first use
importlib.reload(find_dem)
importlib.reload(dem_streamlines)

parent = iface.mainWindow()

if not QgsProject.instance().fileName():
    print('No project is loaded yet')
    prj_fn, prjOK = QFileDialog.getOpenFileNames(parent, "Open a project file", QgsProject.instance().homePath(),
                                                 "Project Files (*.qgz)")
    if prjOK:
        QMessageBox.information(parent, "Success", "Opening {}...".format(prj_fn))
        print('Loaded: ', prj_fn[0])
        QgsProject.instance().read(prj_fn[0])
    else:
        QMessageBox.warning(parent, "Warning", "No project file selected, the process needs a project to work")
else:
    print('Project filepath:', QgsProject.instance().fileName())

prjpath = ntpath.split(QgsProject.instance().fileName())[0] + '/'
os.chdir(prjpath)  # Makes the current working directory match the project directory.

#Run the modules
input_rasters, layer_types = find_dem.find_dem_raster(prjpath)

for raster in input_rasters:
    dem_style.make_terrain(raster, prjpath)
    #If there is other stuff to do, put it here