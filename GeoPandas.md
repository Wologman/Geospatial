The GeoPandas library works with GeoDataFrames.  These behave much like regular Panadas DataFrames, and have similar methods, except that they are able to contain spatial data, with structures inherited from the Shapely package, and include spatial attributes such as the CRS.

GeoPandas can conveniently read data in from a variety of vector spatial file types, including .shp and GeoJSON.  Using `geo_df = read_file(filepath)` We can perform spatial joins and spatial methods on the GeoSeries objects such as `area()` & `centroid()` for example, as well as using most of the usual familiar methods from Pandas, like `sortvalues()`.

## GeoDataFrames
For anything more complex than points, we should use GeoPandas, and create a GeoDataFrame.  Either by directly reading a vector file with `geo_df = read_file(filepath)`, or by creating one from scratch.

Each GeoDataFrame will have a `geometry` field, that will contain a geometry type inhereted from Shapely.  Points, LineStrig, MultiLineString, Polygon, MultiPolygon.

We could build a GeoDataFrame from scratch, by assigning a CRS, and creating the Shapely geometry objects for each row.

## Plotting 

### Scatter plot for point objects
If we just want to plot a bunch of points given latitude and longitude we can use `matplotlib.scatter()`  with longitude on the x axis, latitude on the y.

If the source CSV or DataFrame doesn't alread have a column for lat and long, then some text manipulation is needed.  For a tuple to two columns use a list comprehension.  For example if lotction was in a tuple column named *location*:
```python
bus_stops['lat'] = [loc[0] for loc in bus_stops.Location]
bus_stops['lng'] = [loc[1] for loc in bus_stops.Location]
```
If the lat and longitude is tied up in a more complex structure cosider using a regular expression.

To plot, with nice circles, one color for the face, one for the edge:
```python
plt.scatter(schools.Longitude, schools.Latitude,
markerfacecolor='darkgreen', markeredgecolor='black', marker='p')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Nashville Public Schools')
plt.grid()
plt.show()
```
We could turn the points into shapely point objects, and create a GeoDataFrame, but this isn't necessary if all we want to do is visualise the relative locations of a few points compared to each other.

### Plotting Lines & Polygons
GeoDataFrames have a `.plot()` method that we can use for lines and polygons.
To add scatter plots over the same plot, we simply add the scatter plot to it, as we would with `plt.scatter()`.  Here is an example with both polygons and points:

```python
school_districts.plot(column = 'district', legend = True, cmap = 'Set2')
plt.scatter(schools.lng, schools.lat, marker = 'p', c = 'darkgreen')
plt.title('Nashville Schools and School Districts')
plt.show();
```
The `column` attribute tells the method what column to base the color scheem on.  In this case we are coloring each district a different color, and we are using a categorical color scheme, rather than a continuously variable one.

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