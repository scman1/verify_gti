#
# Preprocessing of sheets before segmentation
#

from pathlib import Path
from  processgti.microscopygtiv import *

# Directory containing the new set of segmented images
source_dir = Path(Path().absolute().parent, "microscopeslides","kew","originals200")
# Directory for processing and verifying the new set of segmented images
work_dir = Path(source_dir, "rotated")
# 1. rotate files and save as JPG
print("Rotate Files")
rotate_files(source_dir, work_dir)
list_image_size(work_dir)
### 2. add borders to all images
##print("Add Borders")
##borders_dir = Path(Path().absolute().parent, "microscopeslides","kew", "withborders")
##add_borders(work_dir, borders_dir)
### 4. shrink images to standard size and resolution
###    1169, 1764 for 96 dpi
###     877, 1323 for 72 dpi
print("Resize Images")
resize_dir = Path(Path().absolute().parent, "microscopeslides","kew", "resized")
shrink_images(work_dir, resize_dir, 800, 300)
# verify pixel sizes
print("verify image dimensions")
pixel_sizes(resize_dir, 800, 300)
list_image_size(resize_dir)
