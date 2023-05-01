import operator
import os
from operator import attrgetter

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches

class wardObject:
    def __init__(self, Ward ):
        self.Ward = Ward
# generate matplotlib handles to create a legend of the features we put in our map.
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the color list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles


plt.ion()

# ---------------------------------------------------------------------------------------------------------------------
# in this section, write the script to load the data and complete the main part of the analysis.
# try to print the results to the screen using the format method demonstrated in the workbook

# load the necessary data here and transform to a UTM projection
# wards = gpd.read_file('../Week3/data_files/NI_Wards.shp').to_crs(epsg=32629)
outline = gpd.read_file('../Week2/data_files/NI_outline.shp').to_crs(epsg=2157)

wards = gpd.read_file('../Week3/data_files/NI_Wards.shp').to_crs(epsg=2157)

counties = gpd.read_file('../Week3/data_files/Counties.shp').to_crs(epsg=2157)
countiesDf = pd.DataFrame(counties)
# pd.set_option('display.max_columns', None)
print(countiesDf.head())

join = gpd.sjoin(wards, counties, how='inner', lsuffix='left', rsuffix='right')
df = pd.DataFrame(join) # CREATE A DATAFRAME OF THE JOIN

print("Counties & Wards have matching CRS : ", counties.crs == wards.crs) # test if the crs is the same for roads_itm and counties.

summary = join.groupby(['CountyName'])['Population'].sum()
print("Counties Summary")
print(summary)
print('Number of features in wards: {}'.format(len(wards.index)))
print('Number of features in join: {}'.format(len(join.index)))

clipped = [] # initialize an empty list
for county in counties['CountyName'].unique():
    tmp_clip = gpd.clip(wards, counties[counties['CountyName'] == county]) # clip the roads by county border
    for ind, row in tmp_clip.iterrows():
        #tmp_clip.loc[ind, 'Length'] = row['geometry'].length # we have to update the length for any clipped roads
        tmp_clip.loc[ind, 'CountyName'] = county # set the county name for each road feature
    clipped.append(tmp_clip) # add the clipped GeoDataFrame to the

# pandas has a function, concat, which will combine (concatenate) a list of DataFrames (or GeoDataFrames)
# we can then create a GeoDataFrame from the combined DataFrame, as the combined DataFrame will have a geometry column.
clipped_gdf = gpd.GeoDataFrame(pd.concat(clipped))
clip_total = clipped_gdf['Length'].sum()

print("CLIPPED GDF - ", clipped_gdf)
print('Number of features in wards: {}'.format(len(wards.index)))
print('Number of features in join: {}'.format(len(join.index)))

# ---------------------------------------------------------------------------------------------------------------------
# below here, you may need to modify the script somewhat to create your map.
# create a crs using ccrs.UTM() that corresponds to our CRS
myCRS = ccrs.UTM(29)
# create a figure of size 10x10 (representing the page size in inches
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

# plot the ward data into our axis, using
ward_plot = wards.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')

ax.add_feature(county_outlines)
county_handles = generate_handles([''], ['none'], edge='r')

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)



print("The Ward With the Highest Population : ")
print(df[df.Population == df.Population.max()])

print("The Ward With the Lowest Population : ")
print(df[df.Population == df.Population.min()])


# save the figure
fig.savefig('sample_map.png', dpi=300, bbox_inches='tight')

