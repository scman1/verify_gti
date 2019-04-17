#
# Prepare unlebelled set for use in training
# 1. rename
# 2. add borders
# 3. resize
#

from pathlib import Path
from  processgti.herbariumgtiv import *

base_dir = "herbariumsheets/mnhn/unlabelled"
# Directory containing the new set of segmented images
source_dir = Path(Path().absolute().parent, base_dir)
print(source_dir)
# Directory for processing and verifying the new set of segmented images
work_dir = Path(Path().absolute().parent, base_dir, "to_process")
# 1. rename all files to match the pattern used by the learning script
print("1. rename files")
rename_files(source_dir, work_dir)

# 2. add borders to all images
print("2. Add Borders")
borders_dir = Path(Path().absolute().parent, base_dir, "with_borders")
add_borders2(work_dir, borders_dir)
# 3. shrink images to standard size and resolution
#    1169, 1764 for 96 dpi
#     877, 1323 for 72 dpi
print("3.1 resize images")
resize_dir = Path(Path().absolute().parent, base_dir, "resized")
shrink_images(borders_dir, resize_dir, max_width_96, max_height_96)
# verify pixel sizes
print("3.2 verify image dimensions")
pixel_sizes(resize_dir, max_width_96, max_height_96) #
list_image_size(resize_dir)
