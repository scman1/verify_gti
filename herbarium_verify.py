#
# Preprocessing and verification before training
#

from pathlib import Path
from  processgti.herbariumgtiv import *

# Directory containing the new set of segmented images
source_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","b_03_test")
# Directory for processing and verifying the new set of segmented images
work_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","b_03_test", "to_process")
# 1. rename all files to match the pattern used by the learning script
print("1. rename files")
rename_files(source_dir, work_dir)

# 2. verify if new set contains already used used images and
#    if so, move them to another directory
# Directory containing the already used set of segmented images (renamed and formated)
##used_dir = Path(Path().absolute().parent, "herbariumsheets", "TrainingHerbariumSheets0296dpi")
##exclude_used(work_dir, used_dir)

# 3. add borders to all images
print("2. Add Borders")
borders_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","b_03_test", "withborders")
add_borders2(work_dir, borders_dir)
# 4. shrink images to standard size and resolution
#    1169, 1764 for 96 dpi
#     877, 1323 for 72 dpi
print("3.1 resize images")
resize_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","b_03_test", "resized")
shrink_images(borders_dir, resize_dir, max_width_96, max_height_96)
# verify pixel sizes
print("3.2 verify image dimensions")
pixel_sizes(resize_dir, max_width_96, max_height_96) #
list_image_size(resize_dir)
# 5. verify and correct label colours (solid blue, red, yellow, white, and black)
print("4 verify label colours")
colour_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","b_03_test", "colourcorrect")
verify_label_colours(resize_dir, colour_dir)
# 6. verify that instances and labels match 
# 6.1 make instance backgrounds black
#     corrected instance backgrounds that were not black
print("5.1 verify instances backgrounds")
verify_instance_backgrounds(colour_dir)
# 6.2 verify that background areas of instances and labels match
#     correct instances or labels as needed
#     instances were larger than labels so growing instances did not work
#     used  positions of labels and instances to create new labels that match
#     instance sizes
print("5.2 verify that instances and labels match")
verify_instance_labels_match(colour_dir)
# 7. after new labels created need to verify label colours again
print("6 verify label colours")
manualedit_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","b_03_test", "manualedit")
verify_label_colours(colour_dir, manualedit_dir)
# 8. after manual edit verify label colours, instance backgrounds,
#    instance-labels match
print("7 final verifications")
finished_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","b_03_test", "finalpass")
print("7.1 label colours")
verify_label_colours(manualedit_dir, finished_dir)
print("7.2 instance backgrounds")
verify_instance_backgrounds(finished_dir)
print("7.3 instance-label match")
verify_instance_labels_match(finished_dir)
# 9. rewrite all pngs, eliminate alpha channel if it was added on manual edit
print("rewrite pngs, remove alpha channels if present")
rezise_png_images(finished_dir)
#10. check pixel dimensions
print("final image dimension check")
list_image_size(finished_dir)
