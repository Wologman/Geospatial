# Module to find select a DEM, import if if need be, and return it as a Rasterlayer object.
# If the layer is in a Geographic Coordinate System, it is projected to NGZD2000
from qgis.utils import iface
import ntpath, sys, os
from qgis.core import QgsProject, QgsMapLayer
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox
import processing

def rpj_rstr(rslt_pth, rstr, in_crs, out_crs):
    rpj_param = {'INPUT': rstr,
        'SOURCE_CRS':in_crs, # 
        'TARGET_CRS':out_crs , #
        'RESAMPLING': 3, # 2=cubic, 3=cubic spline, there are others
        'DATA_TYPE': 6, # Float32
        'OUTPUT':''}
    rpj_param['OUTPUT'] = rslt_pth + 'rpj_' + rstr.name() + '.tif'
    
    processing.run('gdal:warpreproject', rpj_param)
    return rpj_param['OUTPUT']  # Returns a filepath of the reprojected raster
    
def find_dem_raster(prj_pth):
    parent = iface.mainWindow()
    layers = QgsProject.instance().mapLayers() #returns a dict, keys are a unique sequence, values are the layer object
    bOK = False
    rslt_pth = prj_pth + 'Results/'  # Need a check in here, to make sure the dir is there, or add it
    print(rslt_pth)
    
    all_rasters, raster_list, fns, lyr_types = [],[],[],[]
    for lyr in layers.values(): 
        if lyr.type() == QgsMapLayer.RasterLayer:
            all_rasters.append(lyr.name())  # make a list of the raster layer names
    #print('Raster layers present: {}'.format(all_rasters))

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
            
            # Delete any existing files with the same names.  Does the job but not very Pythonic.
            for lyr in layers.values():
                if lyr not in raster_list:
                    for raster in raster_list:
                        if lyr.name() == raster.name():
                            QgsProject.instance().removeMapLayer(lyr)
        else:
            QMessageBox.warning(parent, "Warning", "No file selected")
    
    # Reproject the chosen layer if necessary from a GCS to a PCS
    for lyr in raster_list:
        crs = lyr.crs()
        if crs.isGeographic():
            layer_name = lyr.name()
            rpj_lyr = rpj_rstr(rslt_pth, lyr, crs, 'EPSG:2193')  #Reprojects to NZGD 2000
            QgsProject.instance().removeMapLayer(lyr) #remove old one from canvas
            raster_list.remove(lyr)# remove lyr object from raster_list
            iface.addRasterLayer(rpj_lyr, layer_name) #open the new one, and give original name
            rpj_lyr = QgsProject.instance().mapLayersByName(layer_name) #can be done with the line above?
            raster_list.append(rpj_lyr[0]) # Add the reprojected layer to raster_list
    return raster_list, lyr_types