import os
import matplotlib.pyplot as plt
import geopandas as gpd

from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.ion()  # make the plotting interactive

def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the color list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

def scale_bar(ax, location=(0.92, 0.95)):
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    ax.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=ax.projection)
    ax.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=ax.projection)
    ax.plot([sbx-10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=ax.projection)

    ax.text(sbx, sby-4500, '20 km', transform=ax.projection, fontsize=8)
    ax.text(sbx-12500, sby-4500, '10 km', transform=ax.projection, fontsize=8)
    ax.text(sbx-24500, sby-4500, '0 km', transform=ax.projection, fontsize=8)




# load the outline of Northern Ireland for a backdrop
outline = gpd.read_file('../Week2/data_files/NI_outline.shp').to_crs(epsg=2157)

wards = gpd.read_file('../Week3/data_files/NI_Wards.shp').to_crs(epsg=2157)

counties = gpd.read_file('../Week3/data_files/Counties.shp').to_crs(epsg=2157)
join = gpd.sjoin(wards, counties, how='inner', lsuffix='left', rsuffix='right')
summary = join.groupby(['CountyName'])['Population'].sum()

myMap = plt.figure(figsize=(10, 10))
myCRS = ccrs.UTM(29)  # create a Universal Transverse Mercator reference system to transform our data.
# NI is in UTM Zone 29, so we pass 29 to ccrs.UTM()

ax = plt.axes(projection=myCRS)  # finally, create an axes object in the figure, using a UTM projection,
# where we can actually plot our data.

# first, we just add the outline of Northern Ireland using cartopy's ShapelyFeature
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w')

xmin, ymin, xmax, ymax = outline.total_bounds
ax.add_feature(outline_feature)  # add the features we've created to the map.

# using the boundary of the shapefile features, zoom the map to our area of interest
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=myCRS)  # because total_bounds
# gives output as xmin, ymin, xmax, ymax,
# but set_extent takes xmin, xmax, ymin, ymax, we re-order the coordinates here.





gridlines = ax.gridlines(draw_labels=True,  # draw  labels for the grid lines
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],  # add longitude lines at 0.5 deg intervals
                         ylocs=[54, 54.5, 55, 55.5])  # add latitude lines at 0.5 deg intervals
gridlines.left_labels = False  # turn off the left-side labels
gridlines.bottom_labels = False  # turn off the bottom labels

scale_bar(ax)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

ward_plot = wards.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')

ax.add_feature(county_outlines)
county_handles = generate_handles([''], ['none'], edge='r')

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)


# save the figure as map.png, cropped to the axis (bbox_inches='tight'), and a dpi of 300
myMap.savefig('map.png', bbox_inches='tight', dpi=300)
