#
# Shrink to 72dpi for testing
#

from pathlib import Path
from  processgti.herbariumgtiv import *

print("Resize Segmented Images")
size96_dir = Path(Path().absolute().parent, "herbariumsheets","sample05", "resized","hs96dpib")
resize72_dir = Path(Path().absolute().parent, "herbariumsheets","sample05","resized", "resized72")
shrink_images(size96_dir, resize72_dir, max_width_72, max_height_72)
# verify pixel sizes
print("verify image dimensions")
pixel_sizes(resize72_dir, max_width_72, max_height_72)
list_image_size(resize72_dir)


##print("Resize Non-Segmented Images")
##size96_dir = Path(Path().absolute().parent, "herbariumsheets","sheets", "resized")
##resize72_dir = Path(Path().absolute().parent, "herbariumsheets","sheets", "resized72")
##shrink_images(size96_dir, resize72_dir, max_width_72, max_height_72)
### verify pixel sizes
##print("verify image dimensions")
##pixel_sizes(resize72_dir, max_width_72, max_height_72)
##list_image_size(resize72_dir)
