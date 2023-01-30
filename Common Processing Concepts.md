
## Running Processing Algorithms
[see here](https://gis.stackexchange.com/questions/278061/getting-the-output-layer-reference-returned-by-processing-tool)
The output of native processing algorithms is a dictionary, containing a reference to an object in memory.  So to get a reference to the object its self, treat it like any other dictionary object, but referencing the dictionary key ['OUTPUT']
```Python 
parameter_dict = {'INPUT': filePath, 'etc', 'OUTPUT': 'TEMPORARY_OUTPUT'}
new_obect = processing.run('native:some_process', parameter_dict)['OUTPUT']
```
Note: May be different for other providers, like SAGA, Grass etc, investigate further.

## PyQGIS workflow
With scripting it isn't really necessary to add the intermediate working layers to the map canvas, just leave them in memory, reference as Python objects and deliver the end product.  However for the purpose of testing code and see what is happening add this line:
```python
import QgsProject

QgsProject.instance().addMapLayer(my_layer, True)
print('done')
```
The delete or move it to the next problem when it is no longer of interest.