# Written by Olly Powell
# I wrote this because my laptop can't deal with big LIDAR datasets from LINZ.
# The user choses the tiles of interest from the index shape file, then the
# code here finds the associated data files and copies them to a seperate dir.
  
# Process:
#1. Put this file in the same folder as the mxd 
#2. Download a LINZ tile index shape file, and all associated data tiles
#3. Put the data tiles in a folder named /source-tiles, under same dir as the mxd
#4. Add the tiles, and a basemap
#5. Select the tiles of interest
#6. Open the attribute table
#7. Export selected features to Selection_Attribute_Table.txt in same dir as mxd
#8. Run code
 
date = '2008'  # This may need changing for other datasets!

import shutil
import fnmatch
import os
import pandas as pd

target_dir_path = os.path.dirname(os.path.realpath(__file__)) + '\selected-tiles'
source_dir_path = os.path.dirname(os.path.realpath(__file__)) + '\source-tiles'
all_files = os.listdir(source_dir_path)
if os.path.isdir(target_dir_path):   
    shutil.rmtree(target_dir_path)   #Delete the target directory if it exists

os.mkdir(target_dir_path)
print('Source directory: ', source_dir_path)
print('Number of files in source directory: ', len(all_files))

selected_files = []
selected_tiles = 0
file_list = []

df = pd.read_csv("Selection_Attribute_Table.txt")
print('\n4 rows of the original attribute table: \n')
print(df.head(4), '\n')

def file_id (row):
    name = row['TileName']
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
    src = source_dir_path + '\\' + file
    tgt = target_dir_path + '\\' + file
    shutil.copyfile(src, tgt)
    files_copied +=1

print(files_copied, 'files copied to', target_dir_path)