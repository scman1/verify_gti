#
# Seed the segmented image set with modified images
# blurred, bright, dark and noise
# For testing detection using matlab functions
# split the set 150 - 100
# copy 150 to one directory, including its segments and GTs
# copy 100 to another directory, including its segments and GTs
# from the 100 get 24 random and modify them for testing detection#

from pathlib import Path
from shutil import copyfile, copy
import glob
import random
from  processgti.herbariumgtiv import *

# Blur image by applying Median Blur function
def blur_image(img,source_filename, dest_dir):
    median = cv2.medianBlur(img,5)
    cv2.imwrite(str(Path(dest_dir,source_filename.name)),median,params_jpg)

# Brighten image
def brighten_image(img,source_filename, dest_dir):
    new_image = numpy.zeros(img.shape, img.dtype)
    alpha = 1.0 # Simple contrast control
    beta = 50    # Simple brightness control
    new_image = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    cv2.imwrite(str(Path(dest_dir,source_filename.name)),new_image,params_jpg)

# Darken image
def darken_image(img,source_filename, dest_dir):
    new_image = numpy.zeros(img.shape, img.dtype)
    alpha = 1.0 # Simple contrast control
    beta = -50    # Simple brightness control
    new_image = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    cv2.imwrite(str(Path(dest_dir,source_filename.name)),new_image,params_jpg)

# Add noise
def noise_image(img,source_filename, dest_dir):
    m = (20,20,20) 
    s = (20,20,20)
    noise = numpy.zeros(img.shape, img.dtype)
    buff = img.copy()
    cv2.randn(noise,m,s)
    buff=cv2.add(buff, noise, dtype=cv2.CV_8UC3) 
    cv2.imwrite(str(Path(dest_dir,source_filename.name)),buff,params_jpg)


def seed_test_set(source_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    modification = -1 #0 = blur, 1 = brighten, 2 = darken, 3 = noise    
    #1 get the names of 24 random source files
    #2 for each file, do one of the modifications to seed the set 
    for filepath in sorted(source_dir.glob('*.JPG')):
        s_filename = str(filepath)
        img = cv2.imread(str(s_filename), cv2.IMREAD_COLOR)
        modification += 1
        if modification == 0:
            print("blur image, ", filepath.name)
            blur_image(img,filepath, dest_dir)
        elif modification == 1:
            print("brighten image, ", filepath.name)
            brighten_image(img,filepath, dest_dir)
        elif modification == 2:
            print("darken image, ",  filepath.name)
            darken_image(img,filepath, dest_dir)
        elif modification == 3:
            print("noise image, ", filepath.name)
            noise_image(img,filepath, dest_dir)
            modification = -1
    #3 copy the GT masks for the modified files to dest_dir
    #4 get segments of modified files
    #5 copy modifed segments and files to the seeded test directory.
    #6 save log to verify if tests detect outliers
        
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

def random_select_and_copy(howmany, copy_from, copy_to):
    copy_to.mkdir(parents=True, exist_ok=True)
    list_full = []
    rand_smpl = []
    for filename in copy_from.iterdir():
        nameonly = filename.name
        if ".JPG" in nameonly:
            list_full.append(nameonly)#[:-4])
            
    rand_smpl = [ list_full[i] for i in sorted(random.sample(range(len(list_full)), howmany)) ]
    
    for cpy_file in rand_smpl:
        f_from = Path(copy_from,cpy_file)
        f_to = Path(copy_to,cpy_file)
        if f_from.is_file():
            copyfile(str(f_from), str(f_to))
            copyfile(str(f_from).replace(".JPG","_labels.png"),
                 str(f_to).replace(".JPG","_labels.png"))
            copyfile(str(f_from).replace(".JPG","_instances.png"),
                 str(f_to).replace(".JPG","_instances.png"))
    print(rand_smpl)

def copy_not_used(origin_dir, used_dir, not_used_dir):
    not_used_dir.mkdir(parents=True, exist_ok=True)
    list_used = []
    list_not_used = []
    for filename in used_dir.iterdir():
        nameonly = filename.name
        if ".JPG" in nameonly:
            list_used.append(nameonly)
    for filename in origin_dir.iterdir():
        nameonly = filename.name
        if not (nameonly in list_used) and ".JPG" in nameonly:
            list_not_used.append(nameonly)
    for cpy_file in list_not_used:
        f_from = Path(origin_dir,cpy_file)
        f_to = Path(not_used_dir,cpy_file)
        if f_from.is_file():
            copyfile(str(f_from), str(f_to))
            copyfile(str(f_from).replace(".JPG","_labels.png"),
                 str(f_to).replace(".JPG","_labels.png"))
            copyfile(str(f_from).replace(".JPG","_instances.png"),
                 str(f_to).replace(".JPG","_instances.png"))

def get_subset_segments(subset_dir, segment_dir):
    subset_segment = Path(subset_dir,"segments")
    subset_segment.mkdir(parents=True, exist_ok=True)
    list_originals = []
    for filename in subset_dir.iterdir():
        nameonly = filename.name
        if ".JPG" in nameonly:
            list_originals.append(nameonly.replace(".JPG","*"))

    for cpy_file in list_originals:
        f_from = Path(segment_dir,cpy_file)
        f_to = Path(subset_segment,cpy_file)
        for file in glob.glob(str(f_from)):
            print(file)
            shutil.copy(file, str(subset_segment))
            
            
# Directory containing the original set of images and ground truths
originals_dir = Path(Path().absolute().parent, "herbariumsheets","sample05","to_process")
# Directory containing the segments from images and ground truths
segments_dir = Path(Path().absolute().parent, "herbariumsheets","sample05","segments01")

# Directory to copy the 150 subset of images and ground truths
first_subset = Path(Path().absolute().parent, "herbariumsheets","sample05","subset150")
# Directory to copy the 100 subset of images and ground truths
second_subset = Path(Path().absolute().parent, "herbariumsheets","sample05","subset100")
# Directory to copy the 24 subset of images and ground truths (from the 100)
modify_subset = Path(Path().absolute().parent, "herbariumsheets","sample05","subset24")


#random_select_and_copy(100, originals_dir, second_subset)
#copy_not_used(originals_dir, second_subset, first_subset)
#random_select_and_copy(24, second_subset, modify_subset)
#seed_test_set(modify_subset, modify_subset)
#extract_segments_from_gt(modify_subset)
#get_subset_segments(first_subset, segments_dir) #does not work well misses originals with spaces
#get_subset_segments(second_subset, segments_dir) #does not work well misses originals with spaces
