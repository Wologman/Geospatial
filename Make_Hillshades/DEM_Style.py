# A function that takes in a DEM object, creates a nice looking hillshade
from qgis.utils import iface
import processing
from qgis.core import *
from PyQt5.QtGui import QColor
root = QgsProject.instance().layerTreeRoot()
layers = QgsProject.instance().mapLayers() #returns a dict, values = layer object

def make_hillshade(raster, path):
    hs_name = 'hs_' + raster.name()
    
    for layer in layers.values():
        if layer.name() == hs_name:
            print(layer)
            QgsProject.instance().removeMapLayer(layer)
            
    hs_param = {'INPUT': "", 
      'BAND': 1, 
      'COMPUTE_EDGES': False,
      'ZEVENBERGEN': False,
      'Z_FACTOR': 1.0,
      'SCALE': 111120,  # should automate this setting to match the coordinate system
      'AZIMUTH': 315,
      'COMBINED': False,
      'ALTITUDE': 45,
      'MULTIDIRECTIONAL': False,
      'OUTPUT': ""}

    hs_param['INPUT'] = raster.name()
    hs_param['OUTPUT'] = path + hs_name + '.tif'

    processing.runAndLoadResults('gdal:hillshade',hs_param)
    return QgsProject.instance().mapLayersByName(hs_name)[0]
    
def make_symbology(raster):
    stats = raster.dataProvider().bandStatistics(1, QgsRasterBandStats.All)
    min = stats.minimumValue
    max = stats.maximumValue
    colours = ['#005B00', '#1A6E1A','#5C8E4A','#839B60','#AAA776','#D2B48C','#C0C0C0'] # Low to high
    interval = (max-min)/(len(colours)-1)
    values = [min+interval*i for i in range(len(colours)-1)] + [max]
    rmp_lst=[]
    for value, colour in zip(values,colours):
        rmp_lst.append(QgsColorRampShader.ColorRampItem(value, QColor(colour)))
    
    fnc = QgsColorRampShader()  #Create a ramp shader
    fnc.setColorRampType(QgsColorRampShader.Interpolated)   # sets the ramp type to Interpolated
    fnc.setColorRampItemList(rmp_lst)  # puts the list into the QgsColorRampShader
    shader = QgsRasterShader()  #names a variable for the QgsRasterShader
    shader.setRasterShaderFunction(fnc)  # passes the RampShader into the RasterShader
    renderer = QgsSingleBandPseudoColorRenderer(raster.dataProvider(), 1, shader) #Pass the shader into the renderer
    raster.setRenderer(renderer) #Apply the renderer to the raster
    raster.renderer().setOpacity(0.5)

def reorder_lyrs(rstr_lyr,hs_lyr):
    rstr_node = root.findLayer(rstr_lyr)  # Finds the node belonging to the DEM
    hs_node = root.findLayer(hs_lyr)  # Finds the node of the hillshade.
    parent_node = rstr_node.parent()
    if parent_node == root:
        group_idx = root.findLayers().index(rstr_node) # doesn't count empty groups
        group = root.insertGroup(group_idx, rstr_lyr.name())
        for lyr_node in [rstr_node, hs_node]:
            cloned = lyr_node.clone()
            group.addChildNode(cloned)
            root.removeChildNode(lyr_node)
    else:
        rstr_idx = parent_node.findLayers().index(rstr_node)  # The index of the DEM node
        cloned = hs_node.clone()
        parent_node.insertChildNode(rstr_idx+1, cloned)
        parent_node.removeChildNode(hs_node)
        
def make_terrain(input_rasters, prjpath):
    for rstr_lyr in input_rasters:
        hs_lyr = make_hillshade(rstr_lyr, prjpath)
        make_symbology(rstr_lyr)
        reorder_lyrs(rstr_lyr,hs_lyr)