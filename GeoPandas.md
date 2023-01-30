The GeoPandas library works with GeoDataFrames.  These behave much like regular Panadas DataFrames, and have similar methods, except that they are able to contain spatial data, with structures inherited from the Shapely package, and include spatial attributes such as the CRS.

GeoPandas can conveniently read data in from a variety of vector spatial file types, including .shp and GeoJSON.  Using `geo_df = read_file(filepath)` We can perform spatial joins and spatial methods on the GeoSeries objects such as `area()` & `centroid()` for example, as well as using most of the usual familiar methods from Pandas, like `sortvalues()`.

## Plotting 
### Scatter

### Lines & Polygons


## Spatial Joins

```python
gpd.sjoin(blue_region_gdf, black_point_gdf, op = <operation>)
```
The three operations are `within`, `contains`, `intersects`

## GeoSeries Methods

### Change the CRS
```python
my_new_geodataframe = old_dataframe.to_crs(epsg=3587)   
```

Distance, area, centroid etc