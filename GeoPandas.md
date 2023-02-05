The GeoPandas library works with GeoDataFrames.  These behave much like regular Panadas DataFrames, and have similar methods, except that they are able to contain spatial data, with structures inherited from the Shapely package, and include spatial attributes and methods.

GeoPandas can conveniently read data in from a variety of vector spatial file types, including .shp and GeoJSON.  We can perform spatial joins and other spatial methods on the GeoSeries objects such as `area()` & `centroid()` for example, as well as using most of the usual familiar methods from Pandas, like `sortvalues()`, `groupby()` etc.

For raster data, import using the rasterio library, and add to the same plots.  

For vector basemaps, or to output an interactive html product, work with folium.  This is a Python API for the Leafet JavaScript library, and uses OpenStreetMaps as the source maps. 

## GeoDataFrames
For anything more complex than points, we should use GeoPandas, and create a GeoDataFrame.  Either by directly reading a vector file with `geo_df = read_file(filepath)`, or by creating one from scratch.

Each GeoDataFrame will have a `geometry` field, that will contain a geometry type inherited from Shapely.  Points, LineString, MultiLineString, Polygon, MultiPolygon.

We could build a GeoDataFrame from scratch, by assigning a CRS (Using an EPSG number), and creating the Shapely geometry objects for each row, asigning those to the `geometry` field.

From a Pandas DataFrame with lat and long fields to a GeoPandas GeoDataFrame:

Starting with this dataframe `schools`:

|School Name | Latitude  |   Longitude |
|----------|:-------------:|------:|
|A. Z. Kelley Elementary | 36.021 | -86.658 |
|Alex Green Elementary |36.252 |-86.832 |
|Amqui Elementary |36.273|-86.703 |

First turn the spatial data into Shapely points using a lamda function, then create a GeoDataFrame.
```python
from shapely.geometry import Point
schools['geometry'] = schools.apply(lambda x: Point((x.Longitude, x.Latitude)),
axis = 1)
```
Now turn it into a GeoDataframe with the `GeoDataFrame()` method.
```python
import geopandas as gpd

schools_crs = {'init': 'epsg:4326'}
schools_geo = gpd.GeoDataFrame(schools, GeoDataFrame(schools,
													crs = schools_crs,
													geometry = schools.geometry))
```

### Change the CRS
A common situation is that we may want to work in km or metres, but the data has started in EPSG4326 from a WGS84 projection and uses desimal degrees.  So this will need to be converted to EPSG3587 to work in meters.   Or for New Zealand work consider EPSG4167 to use NZGD2000.

To plot in EPSG4167 using latitude and longitude, but make spatial calculations in metres with EPSG3587, the dataframe can be converted, calculations made, results added to the dataframe, then the dataframe CRS converted back.  Or the calculations can be made in a second dataframe, then the results added back (to avoid any small conversion losses)
```python
my_new_geodataframe = old_dataframe.to_crs(epsg=3587)   
```

## Plotting 

### Scatter plot for point objects
If we just want to plot a bunch of points given latitude and longitude we can use `matplotlib.scatter()`  with longitude on the x axis, latitude on the y.

If the source CSV or DataFrame doesn't alread have a column for lat and long, then some text manipulation is needed.  For a tuple to two columns use a list comprehension.  For example if lotction was in a tuple column named *location*:
```python
bus_stops['lat'] = [loc[0] for loc in bus_stops.Location]
bus_stops['lng'] = [loc[1] for loc in bus_stops.Location]
```
If the lat and longitude is burried in a more complex text string consider using a regular expression to retrieve them.

To plot with matplotlib, with nice circles, a grid, one color for the face, one for the edge:
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
The three operations are `within`, `contains`, `intersects`, `disjoint` Intersects and disjoint are obvious enough, is obvious, but within and contains are a bit subtle.
```python
contains_gdf = gpd.sjoin(blue_region_gdf, black_point_gdf, op = 'contains')
```
This means find all the blue regions that contains all the black points.
```python
within_gdf = gpd.sjoin(black_point_gdf, blue_region_gdf, op = 'within')
```
This means find all the black points that are within the blue regions.  Notice the order is switched.  We're still talking about the same points and regions.

The resulting dataframe will have fields suffixed `_left` and `_right` including the index of the right dataframe.

## GeoSeries Methods & Attributes

Since the GeoDataFrame is made up of GeoSeries objects, we can access all the useful spatial methods like distance, area, centroid etc.   Refer to the docs for the [full list](https://geopandas.org/en/stable/docs/reference/geoseries.html)

Here is an example to get the centroids from a df 'school districts', with polygon geometries in the geometry field.
```python
school_districts['center'] = school_districts.geometry.centroid
```
Some useful methods:
- `.distance(anonther_shapely_object)` between the object and some other thing
-  `.fillna([value, method, inplace])`   Fills the NZ with a geometry
- `.clip(mask[, keep_geom_type])`  
- `.rotate(angle[, origin, use_radians)`
- `.buffer(distance[, resolution])`
- `.intersects(other[, align])` Returns a boolean

Useful attributes
- `.crs` Returns the CRS
- `.length` Length of the series geometry, in units of the CRS
- `.area`
- `.centroid`

## Folium

A python API, that builds interactive maps by accessing the Leaflet JavaScript library
```python
import folium
from shapely.geometry import Point
# construct a map centered at the Eiffel Tower
eiffel_location = Point((48.8583736,2.2922926))
eiffel_tower_map = folium.Map(location=eiffel_location, zoom_start = 12)
# display the map
display(eiffel_tower_map)
```

That's it, super easy to display in ipython.  

### Adding overlays

Continuing from above
```python
folium.GeoJson(some_parisian_overlay.geometry).add_to(eifel_tower_map)
display(eiffel_tower_map)
```

### Markers and popups

Add markers iteratively with the `.add_to()` method
```python
for row in schools_in_dist1.iterrows():
	row_values = row[1]
	location = [row_values['lat'], row_values['lng']]
	marker = folium.Marker(location = location)
	marker.add_to(district1_map)
	display(district1_map)
```

To make popups, create a string_variable, representing the html and add that to the marker.
```python
for row in schools_in_dist1.iterrows():
	row_values = row[1]
	location = [row_values['lat'], row_values['lng']]
	popup = '<strong>' + row_values['name'] + '</strong>'
	marker = folium.Marker(location = location, popup=popup)
	marker.add_to(district1_map)
	display(district1_map)
```
So now we can harness the awesome power of GeoPandas, and overlay the resulting spatial information on an interactive web map.  And put calcualted values into point pop-ups if need be.

### Choropleths

A chloropleth is a map showing density or some other numerical value as a color gradient.  

[Find the colormaps here from matplotlib](https://matplotlib.org/stable/tutorials/colors/colormaps.html)

Supposed we already calculated area/density/normalised/means/ counts of something etc for every polygon in a GeoDataFrame.  And we would like to make a Blue-Green chloropleth.

```python
districts_with_counts.plot(column = 'school_density', cmap = 'BuGn', edgecolor = 'black', legend =
plt.title('Schools per decimal degrees squared area')
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.show()
```

Folium maps have a `chloropleth()` method that can asign a color gradient to numerical values for each polygon.  Here is an example much like above.
```python
# Center point and map for Nashville
nashville = [36.1636,-86.7823]
m = folium.Map(location=nashville, zoom_start=10)

# Define a choropleth layer for the map
m.choropleth(
geo_data=districts_with_counts,
name='geometry',
data=districts_with_counts,
columns=['district', 'school_density'],
key_on='feature.properties.district',
fill_color='YlGn',
fill_opacity=0.75,
line_opacity=0.5,
legend_name='Schools per km squared by School District'
)

# Add layer control and display
folium.LayerControl().add_to(m)
display(m)
```

### Exporting Folium maps to the Web

Getting from a Jupyter notebook or Ipython console to html and javascript takes an extra step.  Still looking into this.    

Try this to get started:
https://pythonhow.com/python-tutorial/folium/Web-Mapping-Tutorial-with-Python-and-Folium/

Then make something cool and ad it to my own portfolio page!



