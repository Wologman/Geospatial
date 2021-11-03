# Written by Olly Powell
# I wrote this because my old laptop couldn't deal with big LIDAR datasets from LINZ.
# The user chooses the tiles of interest from the index shape file, then the
# code here finds the associated data files and copies them to a seperate dir.
  
# Process:
#1. Put this file in the python_scripts folder, child of the project dir 
#2. Download a LINZ tile index shape file, and all associated data tiles
#3. Put the data tiles in a folder named source_tiles, child of the project directory
#4. Add the index tiles, and a basemap
#5. Select the tiles of interest
#6. Open the attribute table
#7. Export selected features to a text file in same dir as project
#8. Strip out everything except the tile name and save to a csv in the scratch directory.
#8. Tweak the code to match the form of the filenames
#9. Run code.
#10.Now only the relevent tiles are stored in the directry of interest.  Import using a virtual raster.

# A better way to do this in QGIS would be to use the filenames to build the virtual raster and import directly.

# This is the current form of the filenames:  DEM_CB11_2016_1000_4123.tif    
# This is the current form of the CSV cells:  CB11_1000_4532
 
date = '2016'  # This may need changing for
selection_table = 'selected_tiles.csv' # could change this if need be

import shutil
import fnmatch
import os
import pandas as pd
from pathlib import Path

project_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute()
print(project_dir)

target_dir_path = project_dir / 'selected_tiles'
source_dir_path = project_dir / 'source_tiles'
selection_path = project_dir / 'Scratch' / selection_table


all_files = os.listdir(source_dir_path)

if os.path.isdir(target_dir_path):   
    shutil.rmtree(target_dir_path)   #Delete the target directory if it exists

os.mkdir(target_dir_path)
print('Source directory: ', source_dir_path)
print('Number of files in source directory: ', len(all_files))

selected_files = []
selected_tiles = 0
file_list = []

df = pd.read_csv(selection_path)
print('\n4 rows of the original attribute table: \n')
print(df.head(4), '\n')

def file_id (row):
    name = row[0]
    return 'DEM_' + name[:4] + '_' + date + name[4:] + '.*'

df['file_name'] = df.apply(lambda row: file_id(row), axis = 1) 

print('\n4 rows of the new attribute table: \n')
print(df.head(4), '\n') 

for name in df['file_name']:
    if name:  # Checks for empty strings
        selected_tiles += 1 #Just keeping track of how many tiles
        matches = fnmatch.filter(all_files, name)
        for file in matches:
            selected_files.append(file)

print('Number of selected tiles: ', selected_tiles)        
print('Number of selected files: ',len(selected_files))
print('Files per tile: ', len(selected_files)/selected_tiles)

# Just doing the copying at the end for readability.
files_copied = 0
for file in selected_files:
    src = source_dir_path / file
    tgt = target_dir_path / file
    shutil.copyfile(src, tgt)
    files_copied +=1

print(files_copied, 'files copied to', target_dir_path)