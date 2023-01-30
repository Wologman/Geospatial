### Writing to a .gpkg attribute table
Writing to geopackage tables in editing mode one feature at a time is a really costly process.  I was using  `lyr.startEditing()`  looping through `changeAttributeValue()` and finishing with `lyr.commitChanges()`.  The `changeAttributeValue()` line is very slow.

[Solution found here](https://gis.stackexchange.com/questions/200997/is-there-a-faster-process-to-update-one-column-for-all-features/215464#215464)

Instead make a dictionary of dictionaries first, then write the whole dictionary to the table in one go.

The dict is in the form:
```python
{fid:{field_idx_1:some_attribute, idx_2:some_other_attr,..},next_fid:{..}...}
```

Then to update the layer:
```python
layer.dataProvider().changeAttributeValues(my_dictionary)
```

My process improved from 32 seconds to 0.45 seconds! 

