The GeoPandas library works with GeoDataFrames.  These behave much like regular Panadas DataFrames, and have similar methods, except that they are able to contain spatial data, with spatial types inherited from the Shapely package, and include spatial attributes and methods.

GeoPandas can conveniently read data in from a variety of vector spatial file types, including .shp and GeoJSON.  We can perform spatial joins and other spatial methods on the GeoSeries objects such as `area()` & `centroid()` for example, as well as using most of the usual familiar methods from Pandas, like `sortvalues()`, `groupby()` etc.

For raster data, import using the Rasterio library, and add to the same plots.  

For vector basemaps, or to output an interactive html product, work with folium.  This is a Python API for the Leafet JavaScript library, and uses OpenStreetMaps by default as the source maps (with other tile providers also an option). 

## GeoDataFrames
For anything more complex than points, we should use GeoPandas, and create a GeoDataFrame.  Either by directly reading a vector file with `geo_df = read_file(filepath)`, or by creating one from scratch.

Each GeoDataFrame will have a `geometry` attribute, that will contain a geometry type inherited from Shapely.  Points, LineString, MultiLineString, Polygon, MultiPolygon.  Typically this will also be a field in the dataframe table named 'geometry', but actually this could be called anything, and would still be a `.geometry` attribute of the dataframe.

We could build a GeoDataFrame from scratch, by assigning a CRS (Using an EPSG number), and creating the Shapely geometry objects for each row, asigning those to the `geometry` field.

From a Pandas DataFrame with latitude and longitude fields to a GeoPandas GeoDataFrame:

Starting with this dataframe `schools`:

|School Name | Latitude  |   Longitude |
|----------|:-------------:|------:|
|A. Z. Kelley Elementary | 36.021 | -86.658 |
|Alex Green Elementary |36.252 |-86.832 |
|Amqui Elementary |36.273|-86.703 |

First turn the spatial data into Shapely points using a lambda function, then create a GeoDataFrame.
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

### `gdp.read_file()`
This is the easiest way to get a geodataframe.  Will read the usual vector dataformats, including .shp, .geojson, .gpkg.   Return a geoDataFrame.

```python
trees = gpd.read_file(paris_trees.gpkg)
```

### Change the CRS
A common situation is that we may want to work in km or metres, but the data has started in EPSG4326 from a WGS84 projection and uses decimal degrees.  So this will need to be converted to EPSG3587 to work in meters.   Or for New Zealand work consider EPSG4167 to use NZGD2000.

To plot in EPSG4167 using latitude and longitude, but make spatial calculations in metres with EPSG3587, the dataframe can be converted, calculations made, results added to the dataframe, then the dataframe CRS converted back.  Or the calculations can be made in a second subset dataframe, then the results added back (to avoid any small conversion losses, and possibly reduce the processing time)
```python
my_new_geodataframe = old_dataframe.to_crs(epsg=3587)   
```

### Data Exploration
Geodataframes inheret most of the methods from regular pandas dataframes, which can be used for convenient analysis.

#### Filtering
We can filter the dataframe by creating a boolean series and using it as a mask.  For example with a dataframe of countries of the world:
```python
countries['continent'] == 'Africa'  #returns a boolean series.  
# Or to use the series as a mask and return only the countries in Africa:
countries_africa = countries[countries['continent'] == 'Africa']
```
The same pattern can be used for spatial queries, to efficiently filter elements based on a spatial relationship.  For example 
```python
cities.within(france)  # This would return a boolean series for a dataframe of cities and a polygon object france.
cities[cities.within(france)] # This would return  a gdb of cities within france
```
Same thing, but here we're going to make it a bit clearer using a mask object on.  Asking which countries intersect with tributaries of the Amazon.  The countries and rivers are in different dataframes.
```python
rivers= geopandas.read_file(my_amazon_rivers_centrelines.gpkg)
# Contains a 'name' field, we're looking for ones called 'Amazonas' with this filter:
amazon = rivers[rivers['name']== 'Amazonas'].geometry.squeeze() 
mask = countries.intersects(amazon) #creating another mask
countries[mask]

>>>  name       continent       geometry
>>>  Brazil     South America   POLYGON((...))
>>>  Columbia
>>>  Peru       etc...
```

#### `.groupby()`

Groupby can be used as usual to get statistics about groups by their common attributes
```python
restaurants = geopandas.read_file("paris_restaurants.geojson")
# Calculate the number of restaurants of each type
type_counts = restaurants.groupby('type').size()
print(type_counts)

>>>     type 
>>> 	African     138
>>> 	Asian       1642
>>> 	Trad French 1945
>>> 	etc...
```

### `pd.merge()`
This is likely to crop up as a useful thing to do after running some kind of calculation, for example a groupby and count, back into the original dataframe.  So it's not a spatial operation, just a traditional dataframe join based on column values.

Here we've already used groupby and size to get a df trees_by_district

```python
districts_trees = pd.merge(districts, trees_by_district on='district_name')
```

This will add the resulting number of trees back into a dataframe of districts. For some future calculation like density, etc.

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

### `gpd.plot()` and `contextily`

GeoDataFrames have a `.plot()` method that we can use for points, lines and polygons, whatever is in the .geometry attribute of the dataframe.   With no arguments at all, this will produce a basic plot with polygons in bue, white gaps between, or blue lines.   

For a really simple base-map, consider improting `contextily` and using the add_basemap() method.  Here is an example of Paris restaurants, starting from a `csv` file of lat and long points in EPSG4326 (decimal degrees) .
```python
import contextily
import geopandas as gpd
import pandas as pd

df = pd.read_csv("paris_restaurants.csv")
# Convert it to a GeoDataFrame
restaurants = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
ax = restaurants.plot(markersize=1)
contextily.add_basemap(ax)
plt.show()
```
Note, that Contextily assumes the Web Mercator projection (EPSG3857).  The data  will often come in WGS84 - EPSG:4326, or something else entirely. So it will ened converting with the `.to_crs()` method.


### Plot with colors based on attribute values

```python
my_gpd.plot(column = 'some interesting value')
```

### Adding a scatterplot
To add scatter plots over the same plot, we simply add the scatter plot to it, as we would with `plt.scatter()`.  Here is an example with both polygons and points:
```python
school_districts.plot(column = 'district', legend = True, cmap = 'Set2')
plt.scatter(schools.lng, schools.lat, marker = 'p', c = 'darkgreen')
plt.title('Nashville Schools and School Districts')
plt.show();
```
The `column` attribute tells the method what column to base the color scheem on.  In this case we are coloring each district a different color, and we are using a categorical color scheme, rather than a continuously variable one.

### Multi-layered plot(s)
The above principle can be extended to any number of extra layers and multiple plots elegantly with `plt.subplots` and setting the `ax` attribute of plot.  For an example of city points on a polygon map of the world:
```python
fig, ax = plt.subplots(figsize=(12,6), nrows=1)  
#nrows is optional, could set nrows=2 and ax[0], ax[1] for two plots
countries.plot(ax=ax)
cities.plot(ax=ax, color='red', markersize=10)
ax.set_axis_off()  #removes the outer border and ticks
plt.show()
```

Here is an example with two plots.
```python
# Set up figure and subplots
fig, axes = plt.subplots(nrows=2)
# Plot equal interval map
districts_trees.plot(column='n_trees_per_area', scheme='equal_interval', k=5, legend=True, ax=axes[0])
axes[0].set_title('Equal Interval')
axes[0].set_axis_off()

# Plot same map with quantiles scheme
districts_trees.plot('n_trees_per_area', scheme='quantiles', k=5, legend=True, ax=axes[1])
axes[1].set_title('Quantiles')
axes[1].set_axis_off()
plt.show()
```


## Spatial Joins

```python
gpd.sjoin(blue_region_gdf, black_point_gdf, op = <operation>)
```
The three operations are `within`, `contains`, `intersects`, `disjoint` Intersects and disjoint are obvious enough, but `within` and `contains` are a bit subtle.
```python
contains_gdf = gpd.sjoin(blue_region_gdf, black_point_gdf, op = 'contains')
```
This means find all the blue regions that contain all the black points.
```python
within_gdf = gpd.sjoin(black_point_gdf, blue_region_gdf, op = 'within')
```
This means find all the black points that are within the blue regions.  Notice the order is switched.  We're still talking about the same points and regions.

The resulting dataframe will have fields suffixed `_left` and `_right` including the index of the right dataframe.

If only a subset of the columns are needed from the right dataframe, subset that dataframe in the join by specifying the columns.  For example to add just two columns for a country name and polygon geometry to a cities dataframe, where the country is the one that has the city point within it's polygon:

```python
joined = gpd.sjoin(cities, countries[['name', 'geometry'], op='within'])
```
Note that it won't work without the geometry field, otherwise the second DataFrame is just a padas DataFrame, not a geoDataFrame!

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

We can also return new geometries.

```python
intersection = park_boulogne.intersection(muette) #intersection of two polygons
#To plot, convert to a geoSeries
geopandas.GeoSeries([intersection]).plot()
plt.show()

# Or work directly with the resulting geometry (a shapely Polygon object)
# Print proportion of district area that occupied by Park Boulogne:
print(intersection.area / muette.area)
```

A common use of this would be to subset a spatial dataset with a simple polygon, like a circle or rectangle, to reduce the scope of the data, or present only the bits we want.  In this case, we get left with a dataframe with the same number of rowsm but empty polygons for the features that did not intersect.  In general:

```python
my_new_geoseries = my_geoseries.intersection(my_polygon)
```

### Overlays
Intersection is the simple method for a polygon with a dataset.  But where we have two datasets, and we want to create a third with all polygons of one, intersecting with all polygond of another (for example a countries df with a land-use dataframe, might be interesting, so you end up with french-wheat, french-industrial, german-wheat, german-industrial etc...)  And keep the attributes from both datasets in the new one.  This is when to use overlays.




## Folium

A python API, that builds interactive maps by accessing the Leaflet JavaScript library
```python
import folium
from shapely.geometry import Point
# construct a map centered at the Eiffel Tower
eiffel_location = Point((48.8583736,2.2922926))
eiffel_tower_map = folium.Map(location=eiffel_location, zoom_start = 12)
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

A chloropleth is a map showing density or some other numerical value as a color gradient applied to each region (polygon).   [Find the colormaps here from matplotlib](https://matplotlib.org/stable/tutorials/colors/colormaps.html)

Supposed we already calculated area/density/normalised values/means/ counts of something etc. for every polygon in a GeoDataFrame.  And we would like to make a Blue-Green chloropleth.

```python
districts_with_counts.plot(column = 'school_density', 
						   cmap = 'BuGn', edgecolor='black', legend=True)
plt.title('Schools per decimal degrees squared area')
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.show()
```

It is also possible to create a coropleth with a continuous variable, by assigning a number of bins, and a quantisation scheme.  Use `quantiles` for variables with a very uneven distribution of data,  otherwise `equal_interval`.  

```python
locations.plot(column='variable', scheme='equal_interval', k=7, cmap='Purples')
```

For categoricals we can use a non-ordered color scheme, for example `Purples` .  For a graduated variable use a sequential color scheme like `RdPu`.  And for a graduated variable where there is a typical value around the median, but you would like to illistrate areas diverging from that, use a diverget scheme like `RdYlGn`

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
By default folium uses Open Street Map, but there is a argument `tiles` that can be set to other sources the full list below:

-   OpenStreetMap
-  Mapbox Bright” (Limited levels of zoom for free tiles)
-   Mapbox Control Room (Limited levels of zoom for free tiles)
-   Stamen (Terrain, Toner, and Watercolor)
-   Cloudmade (Must pass API key)
-   “Mapbox” (Must pass API key)
-   “CartoDB” (positron and dark_matter)

### Exporting Folium maps to the Web

Add a a save method at the end,  `map.save(outfile='my_awesome_map.html')`  Then put the resulting javascript, html and css onto the website.  That's it!  So easy :)

## Saving Geopandas Dataframes as files

For this we use the GDAL `.to_file` method.  And we need to specify the driver as well as the appropriate file name.    Supports geojson, gpkg & shp (but only use .shp under duress)

```python

geodataframe.to_file('my_geo_file.geojson' driver='GeoJSON')
geodataframe.to_file('my_geo_file.gpkg' driver='GPKG')
```






