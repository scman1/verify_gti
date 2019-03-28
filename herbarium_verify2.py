#
# Preprocessing and verification before training
#

from pathlib import Path
from  processgti.herbariumgtiv import *

### Directory containing the new set of segmented images
##source_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","batch_3")
### Directory for processing and verifying the new set of segmented images
##work_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","batch_3", "to_process")
### 1. rename all files to match the pattern used by the learning script
##print("1. rename files")
##rename_files(source_dir, work_dir)
##
### 2. add borders to all images
##print("2. Add Borders")
##borders_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","batch_3", "with_borders")
##add_borders2(work_dir, borders_dir)
### 3. shrink images to standard size and resolution
###    1169, 1764 for 96 dpi
###     877, 1323 for 72 dpi
##print("3.1 resize images")
##resize_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","batch_3", "resized")
##shrink_images(borders_dir, resize_dir, max_width_96, max_height_96)
### verify pixel sizes
##print("3.2 verify image dimensions")
##pixel_sizes(resize_dir, max_width_96, max_height_96) #
##list_image_size(resize_dir)
### 4. verify that instances and labels match
##print("4.1 verify instances borders")
### 4.1 make instance borders black
##verify_instance_borders(resize_dir)
### 4.2 make instance backgrounds black
###     corrected instance backgrounds that were not black
##print("4.2 verify instances backgrounds")
##verify_instance_backgrounds(resize_dir)
### 4.3 verify that background areas of instances and labels match
###     correct instances or labels as needed
###     instances were larger than labels so growing instances did not work
###     used  positions of labels and instances to create new labels that match
###     instance sizes
##print("4.3 verify that instances and labels match")
##verify_instance_labels_match(resize_dir)
### 5. after new labels created need to verify label colours again
##print("5 verify label colours")
manualedit_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","batch_3", "nmw_full_set")
##verify_label_colours(resize_dir, manualedit_dir)
# 6. after manual edit verify label colours, instance backgrounds,
#    and instance-labels match
print("6 final verifications")
finished_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","batch_3","nmw_final_pass1")
print("6.1 label colours")
verify_label_colours(manualedit_dir, finished_dir)
print("6.2 instance backgrounds")
verify_instance_backgrounds(finished_dir)
print("6.3 instance-label backgrounds match")
verify_instance_labels_match(finished_dir)
#verify_instance_labels_match(finished_dir)
# 9. rewrite all pngs, eliminate alpha channel if it was added on manual edit
print("rewrite pngs, remove alpha channels if present")
rezise_png_images(finished_dir)
#10. check pixel dimensions
print("final image dimension check")
list_image_size(finished_dir)
finished2_dir = Path(Path().absolute().parent, "herbariumsheets","nmw","batch_3","nmw_final_pass2")
print("10.1 label colours")
verify_label_colours(finished_dir, finished2_dir)
##verify_instance_labels_match(finished2_dir)
