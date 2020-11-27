# Module to find select a DEM, import if if need be, and return it as a Rasterlayer object.
from qgis.utils import iface
import ntpath, sys, os
from qgis.core import QgsProject, QgsMapLayer
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox

parent = iface.mainWindow()
layers = QgsProject.instance().mapLayers() #returns a dict, keys are a unique sequence, values are the layer object

def find_dem_raster():
    bOK = False
    all_rasters, raster_list, fns, lyr_types = [],[],[],[]
    for lyr in layers.values(): 
        if lyr.type() == QgsMapLayer.RasterLayer:
            all_rasters.append(lyr.name())       # make a list of the raster layer names
    # print('Raster layers present: {}'.format(all_rasters))

    if all_rasters: 
        # If the all_rasters is not empty, choose from the raster list
        all_rasters.append('Search for file')
    
        chosen_raster, bOK = QInputDialog.getItem(parent, "DEM styling script", "Choose a DEM", all_rasters, editable=False)
        if bOK:
            if chosen_raster == 'Search for file': 
                bOK = False
            else:
                #print('Raster Chosen: {}'.format(chosen_raster))
                chosen = QgsProject.instance().mapLayersByName(chosen_raster)
                raster_list.append(chosen[0])
                lyr_types.append(type(chosen[0]))
            
    def base_name(path):   # A function to split out the file name from the full path.
        head, tail = ntpath.split(path)
        return tail.split('.')[0] or ntpath.basename(head.split('.')[0])

    if not bOK:  # Go browse for the files if none chosen
        fns, fnOK = QFileDialog.getOpenFileNames(parent,"Raster File(s) to Open", QgsProject.instance().homePath(),
                                                 "TIFF & Geo TIFF Files (*.tif)")
        if fnOK:
            QMessageBox.information(parent, "Success", "Opening {}...".format(fns))
            for fn in fns:
                layer_name = base_name(fn)
                iface.addRasterLayer(fn, layer_name)
                lyr = QgsProject.instance().mapLayersByName(layer_name)
                #add the raster object here by filename to the raster_list
                raster_list.append(lyr[0])
                lyr_types.append(type(lyr[0]))
        else:
            QMessageBox.warning(parent, "Warning", "No file selected")
    
    return raster_list, lyr_types
    