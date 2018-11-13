# Verify if files in directory have been used for training
# Need training dataset directory and samples directory as input
# non used files will be copied to a sub directory under samples
from pathlib import Path
from shutil import copyfile
import random

def listnotused(training_dir, samples_dir):
    list_full = []
    for filename in training_dir.iterdir():
        list_full.append(filename.name)
    print("Image total: ", len(list_full))

    list_validate = []
    for filename in samples_dir.iterdir():
        nameonly = filename.name 
        if "labels" not in nameonly and "instances" not in nameonly:
            list_validate.append(filename.name)

    print("Segmented images: ",len(list_validate))

    list_not_used = list(set(list_full) ^ set(list_validate))

    print("Not used images:", len(list_not_used))

    return list_not_used

#need a new version because only part of the name may match the pattern
def listnotused2(training_dir, samples_dir):
    list_used = []
    for filename in training_dir.glob("*.jpg"):
        list_used.append(filename.name[:-4].replace(" ","_"))
    print("Image total: ", len(list_used))

    list_found =[]
    for workfile in list_used:
        instance_file = sorted(samples_dir.glob("*"+workfile+"*"))
        if not not instance_file:
            list_found.append(list(instance_file)[0].name)
            
    print("Used images:", len(list_found))
    list_not_used = []
    for filename in samples_dir.glob("*"):
        nameonly = filename.name
        if not nameonly in list_found or not list_found:
            list_not_used.append(nameonly)

    print("Image total: ", len(list_not_used))
    return list_not_used

#random list of unused images to build new training set
def randomsample(samples_list, sample_size):
    rand_smpl = [samples_list[i] for i in sorted(random.sample(range(len(samples_list)), sample_size)) ]
    print(rand_smpl)
    return rand_smpl


def copysample(samples_dir, file_list):
    dest_dir = Path(samples_dir,'new_sample')
    dest_dir.mkdir(parents=True, exist_ok=True)
    for cpy_file in file_list:
        #print("copy:",  str(Path('..','slides','nhm_standard',cpy_file)), "to:", str(Path('..','slides', 'nhm_std_unused',cpy_file)))
        f_from = Path(samples_dir,cpy_file)
        f_to = Path(dest_dir,cpy_file)
        if f_from.is_file():
            copyfile(str(f_from),
                     str(f_to))
        
def get_original_filename(instance_file, source_dir):
    workfile = instance_file.name.replace("_instances.png","")
    workfile = workfile.replace("_","*")
    source_file = source_dir.glob("*"+workfile+"*.jpg")
    return list(source_file)[0]
                             
# Directory containing the used images
used_dir = Path(Path().absolute().parent, "herbariumsheets","sample05")
# Directory containing the new sample
notused_dir = Path(Path().absolute().parent, "herbariumsheets","MeiseSamples", "DOMeiseSamples")

#get a list of all non used files on the larger list pool
notusedlist = listnotused2(used_dir, notused_dir)

#get a random sample from the non used list to create a new test set
randomlist = randomsample(notusedlist, 50)

copysample(notused_dir, randomlist)



