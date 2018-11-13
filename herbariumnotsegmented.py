#
# Preprocessing of sheets before segmentation
#

from pathlib import Path
from  processgti.herbariumgtiv import *

# Directory containing the new set of segmented images
source_dir = Path(Path().absolute().parent, "herbariumsheets","sheets")
# Directory for processing and verifying the new set of segmented images
work_dir = Path(Path().absolute().parent, "herbariumsheets","sheets", "to_process")
# 1. rename all files to match the pattern used by the learning script
#    no spaces, JPG extension
print("Rename Files")
rename_files(source_dir, work_dir)

# 2. add borders to all images
print("Add Borders")
borders_dir = Path(Path().absolute().parent, "herbariumsheets","sheets", "withborders")
add_borders(work_dir, borders_dir)
# 4. shrink images to standard size and resolution
#    1169, 1764 for 96 dpi
#     877, 1323 for 72 dpi
print("Resize Images")
resize_dir = Path(Path().absolute().parent, "herbariumsheets","sheets", "resized")
shrink_images(borders_dir, resize_dir, max_width_96, max_height_96)
# verify pixel sizes
print("verify image dimensions")
pixel_sizes(resize_dir, max_width_96, max_height_96)
list_image_size(resize_dir)
