#
# Ground thruth image files verfication preprocessing
# A set of procedures for  verifying that the ground truth datasets
# are suitable for training  NHM semantic segmentation network
# 
# Initial version 2018-05-29, for verifying microscope slides
# Current version 2018-08-17, for veifying herbarium sheets
# GitHub  version 2018-09-06, initial check in
#
# Author: Abraham Nieva de la Hidalga
# Project: ICEDIG
#
# Language: Python 3.6.6

from PIL import Image
from pathlib import Path
import cv2
import numpy
import time
import shutil
from collections import Counter

#Values from samples
min_height =  11.2
max_height = 18.3833333333333
min_width = 9.33666666666667 
max_width = 12.1816666666667

#height and width values from bibliography
hs_min_height = 16.5
hs_max_height = 17.096
hs_width = 11.5

# five porcent tolerance on 
tolerance = 0.05

#Standard DPI resolutions 
standard_dpi = [72,96,150,250,300,600]
min_dpi = 72
max_dpi = 600

# parameters for png
# required for removing alpha channel
params_png = list()
params_png.append(cv2.IMWRITE_PNG_COMPRESSION)
params_png.append(8)

# parameters for jpg
# required for preserving quality as much as possible after each transformation
params_jpg = list()
params_jpg.append(cv2.IMWRITE_JPEG_QUALITY)
params_jpg.append(100)

# standard pixel dimensions for 96 dpi
max_width_96=1169
max_height_96=1764

# standard pixel dimensions for 72 dpi
max_width_72=877
max_height_72=1323

def height_in_hs_range(height):
    min_limit = hs_min_height - hs_min_height * tolerance
    max_limit = hs_max_height + hs_max_height * tolerance
    return (min_limit < height and height < max_limit)

def width_in_hs_range(width):
    min_limit = hs_width - hs_width * tolerance
    max_limit = hs_width + hs_width * tolerance
    return (min_limit < width and width < max_limit)

def get_dpi_resolution(width, height):
    dpisxy = []
    dpisy = []
    dpisx = []
    for i in range(min_dpi, max_dpi):
        if height_in_hs_range(height/i) and width_in_hs_range(width/i):
            dpisxy.append(i)
        elif width_in_hs_range(width/i):
            dpisx.append(i)
        elif height_in_hs_range(height/i):
            dpisy.append(i)
    
    found = list(set(standard_dpi) & set(dpisxy) & set(dpisx) & set(dpisy))
    if len(found) > 0:
        return found
    elif len(dpisxy) > 0:
        return int(round(sum(dpisxy)/len(dpisxy)))
    elif len(dpisx)>0:
        return int(round(sum(dpisx)/len(dpisx)))
    elif len(dpisy)>0:
        return int(round(sum(dpisy)/len(dpisy)))
    else:
        return 0

# previuos steps: rename files, change extetion of jpgs
# scan the list of standard dpi and return the one that matches best first
# this is the one used for the first passes of the herbarium processing
def standard_based_dpi(img_height, img_width):
    predicted_dpi = 0  
    for i in standard_dpi:
        calc_width = img_width/i
        if calc_width > min_width*.95 and calc_width < max_width*1.05:
            return i
    if predicted_dpi == 0:
        for i in standard_dpi:
            calc_height = img_height/i
            if calc_height > min_height*.95 and calc_height < max_height*1.05:
                return i
    return 0

def pixels_from_stds(img_height, img_width):
    dpi_predicted=standard_based_dpi(img_height, img_width)
    

    img_width_inch = img_width / dpi_predicted
    img_height_inch = img_height / dpi_predicted
    #print(img_width_inch, img_height_inch)
    
    pix_add_x = int(round((max_width - img_width_inch) * dpi_predicted))
    pix_add_y = int(round((max_height - img_height_inch) * dpi_predicted))
    return dpi_predicted,pix_add_x, pix_add_y

def pixels_calculated(img_height, img_width):
    dpi_predicted=get_dpi_resolution(img_width, img_height)
    
    img_width_inch = img_width / dpi_predicted
    img_height_inch = img_height / dpi_predicted
    #print(img_width_inch, img_height_inch)
    
    pix_add_x = int(round((max_width - img_width_inch) * dpi_predicted))
    pix_add_y = int(round((max_height - img_height_inch) * dpi_predicted))
    return dpi_predicted,pix_add_x, pix_add_y
    
# add borers to all images in source directory and save them to dest directory  
def add_borders(source_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    i=1
    img_dpis = {}
    for source_filename in sorted(source_dir.glob('*.JPG')):
        s_image = str(source_filename)
        img = Image.open(s_image)
        img_width, img_height = img.size
        #try to aproximate from standard sizes 
        dpi_predicted,  pix_add_x, pix_add_y = pixels_from_stds(img_height, img_width)
        
        print (i, source_filename.name,img_width, img_height, dpi_predicted, pix_add_x, pix_add_y)
        img_dpis[s_image] = (i, source_filename.name,img_width, img_height, dpi_predicted, pix_add_x, pix_add_y)
        i=i+1

        # add pixels to original image as black border
        img1 = cv2.imread(s_image)
        resized_img= cv2.copyMakeBorder(img1,0,pix_add_y,0,pix_add_x,cv2.BORDER_CONSTANT,value=0)
        cv2.imwrite(str(Path(dest_dir,source_filename.name)),resized_img)
        # add pixels to instances and labels as black border
        s_instances = s_image.replace(".JPG","_instances.png")
        if Path(s_instances).is_file():
            img_instances = cv2.imread(s_instances)
            resized_instance = cv2.copyMakeBorder(img_instances,0,pix_add_y,0,pix_add_x,cv2.BORDER_CONSTANT,value=0)
            cv2.imwrite(str(Path(dest_dir,source_filename.name.replace(".JPG","_instances.png"))),resized_instance,params_png)
            
        s_labels = s_image.replace(".JPG","_labels.png")
        if Path(s_labels).is_file():
            img_labels = cv2.imread(s_labels)
            resized_labels = cv2.copyMakeBorder(img_labels,0,pix_add_y,0,pix_add_x,cv2.BORDER_CONSTANT,value=0)
            cv2.imwrite(str(Path(dest_dir,source_filename.name.replace(".JPG","_labels.png"))),resized_labels,params_png)
    print(img_dpis)

# shrink images to the specified dpi width and height
def shrink_images(working_dir, width_to, height_to):
    for filepath in sorted(working_dir.glob('*')):
        if "JPG" in filepath.name or "png" in filepath.name:
            #read the image
            img = cv2.imread(str(filepath), cv2.IMREAD_COLOR)
            #get dimensions
            height,width,_ = img.shape
            #get shrink factor
            shrk_factor = width_to/width
            print (filepath.name, width_to,height,width,shrk_factor)
            
            # print source_filename.name, height,width,shrk_factor 
            # rezise image
            res = cv2.resize(img,None,fx=shrk_factor, fy=shrk_factor, interpolation = cv2.INTER_CUBIC)
            # crop image
            if "JPG" in filepath.name:
                cv2.imwrite(str(Path(working_dir,filepath.name)),res,params_jpg)
            elif "png" in filepath.name:
                cv2.imwrite(str(Path(working_dir,filepath.name)),res,params_png)

def pixel_sizes(directory, width_to, height_to ):
    # add one pixel to all sides of poligons
    for filename_ins in sorted(directory.glob('*.JPG')):
        s_filename = str(filename_ins)
        img = Image.open(str(s_filename))
        width,height = img.size
        if height!=height_to or width != width_to:
            print("out of range", filename_ins.name, height, width)

def get_unique_colours(img):
    aimg= numpy.asarray(img)
    return set( tuple(v) for m2d in aimg for v in m2d )


def get_unique_colours_2(img):
    aimg= numpy.asarray(img)
    return numpy.unique(aimg.reshape(-1, aimg.shape[2]), axis=0)

def get_colour_count(img):
    aimg= numpy.asarray(img)
    return Counter([tuple(colors) for i in aimg for colors in i])

# PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
def getcolorlist(img):
    rgb_img = img.convert('RGB') # create the pixel map
    colorlist={}
    for i in range(img.size[0]):    # for every col:
        for j in range(img.size[1]):    # For every row
            r, g, b = rgb_img.getpixel((i,j)) # set the colour accordingly
            color=str(r)+","+str(g)+","+str(b)
            if color in colorlist:
                colorlist[color]+=1
            else:
                colorlist[color]=1
    return colorlist


def exclude_used(dest_dir, used_dir):
    list_full = []
    for file in sorted(dest_dir.glob('*')):
        list_full.append(file.name)
    #print(list_full)
    list_used = []
    for used_file in sorted(used_dir.glob('*')):
        list_used.append(used_file.name)
    # print(list_used)
    # move previously used files to another directory
    ignore=Path(dest_dir,"ignore")
    ignore.mkdir(parents=True, exist_ok=True)
    used_count=0
    for filename in list_full:
        if filename in list_used:
            shutil.move(str(Path(dest_dir,filename)), str(Path(ignore,filename)))
            used_count += 1
        #else:
           #print("not used", filename)
    print("used files in set", used_count)

def correct_label_colours(filename_labels):
    # make all colours either black, white, red or yellow
    # turning any colour channel with less than 100 will to 0
    img_labels = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    height,width,channels = img_labels.shape
    img2 = img_labels
    for i in range(height):
        for j in range(width):
            color = img2[i,j]
            if color[0] < 100:
                color[0] = 0
            else:
                color[0] = 255
            if color[1] < 100:
                color[1] = 0
            else:
                color[1] = 255
            if color[2] < 100:
                color[2] = 0
            else:
                color[2] = 255
            img2[i,j] = color
    cv2.imwrite(str(filename_labels),img2)

def verify_label_colors(dest_dir):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    #counter = 0
    for dest_filename in sorted(dest_dir.glob('*labels.png')):
        s_filename = str(dest_filename)
        img = Image.open(str(s_filename))
        colours = get_colour_count(img)
    #    counter +=1
        if len(colours)>4:
            print(dest_filename.name, colours, len(colours), "needs correcting colours")
            correct_label_colours(dest_filename)
        else:
            print(dest_filename.name, len(colours), "ok")
    #    if counter > 90:
    #        break
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

# change colours with counts smaller than 500 to the background colour
def correct_instance_colors(filename_labels):
    img_instances = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    height,width,channels = img_instances.shape
    

    colorlist=get_colour_count(img_instances)
    #print("initial colour count", len(colorlist))
    #print(colorlist)
    bigcolors ={}
    countuniques = 0
    for color in colorlist:
        if colorlist[color] < 500:
            countuniques += 1
        else:
            bigcolors[color]=colorlist[color]
    img2 = img_instances
    background = (0, 0, 0)
    for i in range(height):
        for j in range (width):
            color = img2[i,j]
            if not (tuple(color) in bigcolors):
                img2[i,j] = background
    cv2.imwrite(str(filename_labels),img2)

def verify_instance_borders(dest_dir):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    #counter = 0
    for dest_filename in sorted(dest_dir.glob('*instances.png')):
        s_filename = str(dest_filename)
        img = Image.open(str(s_filename))
        colours = get_colour_count(img)
    #    counter +=1
        if len(colours)>20:
            #print(dest_filename.name, colours, len(colours), "needs correcting colours")
            print(dest_filename.name, len(colours), "needs correcting colours")
            correct_instance_colors(dest_filename)
        else:
            print(dest_filename.name, len(colours), "ok")
    #    if counter > 90:
    #        break
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

# Directory containing the new set of segmented images
source_dir = Path(Path().absolute().parent, "herbariumsheets","sample02", "ignore")
# Directory for processing and verifying the new set of segmented images
dest_dir = Path(Path().absolute().parent, "herbariumsheets", "sample02b")
# Directory containing the already used set of segmented images
used_dir = Path(Path().absolute().parent, "herbariumsheets", "TrainingHerbariumSheets01")

### 1. verify if new set contains already used used images and
###    if so, move them to another directory
##exclude_used(source_dir, used_dir)
### 2. add borders to all images
##add_borders(source_dir, dest_dir)
### 3. shrink images to standard size and resolution
###    1169, 1764 for 96 dpi
###     877, 1323 for 72 dpi 
##shrink_images(dest_dir, max_width_96, max_height_96)
### verify pixel sizes
##pixel_sizes(dest_dir, max_width_96, max_height_96)
### 4. verify and correct label colors (solid red, white, yellow and black)
##verify_label_colors(dest_dir)
# 5.verify and match instances to labels
# 5.1 correct the borders of the instances
verify_instance_borders(dest_dir)
##
### 6. grow all instances (compensate border correction)
##
### 7. recolor instances backgrounds (make them all light instead of black)
### 8. 
##print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
##counter = 0
##for dest_filename in sorted(dest_dir.glob('*.png')):
##    s_filename = str(dest_filename)
##    img = Image.open(str(s_filename))
##    colours = get_unique_colours(img)
##    print(dest_filename.name, len(colours))
##    counter +=1
##    if counter > 3:
##        break
##
##
##print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
##
##counter = 0
##for dest_filename in sorted(dest_dir.glob('*.png')):
##    s_filename = str(dest_filename)
##    img = Image.open(str(s_filename))
##    colours = get_unique_colours_2(img)
##    print(dest_filename.name, len(colours))
##    counter +=1
##    if counter > 3:
##        break
##
##

##counter = 0
##for dest_filename in sorted(dest_dir.glob('*.png')):
##    s_filename = str(dest_filename)
##    img = Image.open(str(s_filename))
##    colours = getcolorlist(img)
##    print(dest_filename.name, len(colours))
##    counter +=1
##    if counter > 3:
##        break
##
##print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))


# 7. use relative positions of labels and corrected instances to create new
#    labels that match instance sizes


