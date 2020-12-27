#
# Preprocessing and verification before training
#

from pathlib import Path
from  processgti.microscopygtiv import *
slide_width = 800
slide_height = 300
### Directory containing the new set of segmented images
##source_dir = Path(Path().absolute().parent, "slides","kewgt500")
### Directory for processing and verifying the new set of segmented images
##work_dir = Path(Path().absolute().parent, "slides","kewgt500", "to_process")
### 1. rename all files to match the pattern used by the learning script
##print("1. rename files")
##rename_files(source_dir, work_dir)
##
### 2. verify if new set contains already used used images and
###    if so, move them to another directory
### Directory containing the already used set of segmented images (renamed and formated)
####used_dir = Path(Path().absolute().parent, "slides", "Trainingslides0296dpi")
####exclude_used(work_dir, used_dir)
##
### 3. add borders to all images
##print("2. Add Borders")
##borders_dir = Path(Path().absolute().parent, "slides","kewgt500", "withborders")
##add_borders(work_dir, borders_dir)
### 4. shrink images to standard size and resolution
###    800, 300 for 300 dpi
##print("3.1 resize images")
##resize_dir = Path(Path().absolute().parent, "slides","kewgt500", "resized")
##shrink_images(borders_dir, resize_dir, slide_width, slide_height)
### verify pixel sizes
##print("3.2 verify image dimensions")
##pixel_sizes(resize_dir, slide_width, slide_height) #
##list_image_size(resize_dir)
##
### 4. verify that instances and labels match 
### 4.1 make instance backgrounds black
###     correct instance backgrounds that were not black
##print("4.1 verify instances backgrounds")
##verify_instance_backgrounds(resize_dir)
### 4.2 verify that background areas of instances and labels match
###     correct instances or labels as needed
###     instances were larger than labels so growing instances did not work
###     used  positions of labels and instances to create new labels that match
###     instance sizes
##print("4.2 verify that instances and labels match")
##verify_instance_labels_match(resize_dir)
# 5. after new labels created need to verify label colours again
##print("5 verify label colours")
##manualedit_dir = Path(Path().absolute().parent, "slides","kewgt500", "manualedit")
##verify_label_colours(resize_dir, manualedit_dir)
### 6. after manual edit verify label colours, instance backgrounds,
###    instance-labels match
##print("6.1 final verifications")
finished_dir = Path(Path().absolute().parent, "slides","kewgt500", "finalpass")
##verify_label_colours(manualedit_dir, finished_dir)
##verify_instance_backgrounds(finished_dir)
##verify_instance_labels_match(finished_dir)
### 9. rewrite all pngs, eliminate alpha channel if it was added on manual edit
##print("9. rewrite pngs, remove alpha channels if present")
##rezise_png_images(finished_dir)
###10. check pixel dimensions
##print("10. final image dimension check")
##list_image_size(finished_dir)
###11. check label colours again
##print("11. final colour check")
final_a = Path(Path().absolute().parent, "slides","kewgt500", "finalpassd")
##verify_instance_backgrounds(finished_dir)
##verify_instance_labels_match(finished_dir)
##verify_label_colours(finished_dir, final_a)
final_b = Path(Path().absolute().parent, "slides","kewgt500", "finalpasse")
#verify_label_colours(final_a, final_b)
verify_instance_backgrounds(final_b)
verify_instance_labels_match(final_b)
list_image_size(final_b)
