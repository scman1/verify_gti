#
# Ground thruth image files preprocessing and postprocessing functions
# A set of procedures for:
#   a) verifying that ground truth datasets are suitable for training NHM
#      semantic segmentation network (unique colours, instance sizes)
#   b) pre-processing (add borders, resize)
#   c) post-processing (extract segments from original files)
# 
# Initial  version 2018-05-29, for verifying microscope slides
# Extended version 2018-08-17, for verifying herbarium sheets
# GitHub   version 2018-09-06, initial check in to github
# Rewrite  version 2018-10-10, split into library modules 
#
# Author: Abraham Nieva de la Hidalga
# Project: ICEDIG
#
# Language: Python 3.6.6
#
# Why use PIL and CV2?
#    - PIL is faster for pixel by pixel verification
#    - CV2 with numpy is faster if array operations are used
#       using CV2 for pixel by pixel manipulation is really slow
#    - All procedures can be migrated to CV2 eventually

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
params_jpg.append(94)

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
            predicted_dpi = i
    if predicted_dpi == 0:
        for i in standard_dpi:
            calc_height = img_height/i
            if calc_height > min_height*.95 and calc_height < max_height*1.05:
                predicted_dpi = i
    if predicted_dpi == 0:
      predicted_dpi = get_dpi_resolution(img_width, img_height)
    return predicted_dpi

def pixels_from_stds(img_height, img_width):
    
    dpi_predicted=standard_based_dpi(img_height, img_width)
    
    img_width_inch = img_width / dpi_predicted
    img_height_inch = img_height / dpi_predicted
    #print(img_width_inch, img_height_inch)
    ppi_x = round(max_width * dpi_predicted)
    ppi_y = round(max_height * dpi_predicted)
      
    pix_add_x = int(round((max_width - img_width_inch) * dpi_predicted))
    pix_add_y = int(round((max_height - img_height_inch) * dpi_predicted))

    # both width and height larger than standards
    if pix_add_x < 0 and pix_add_y < 0:
        if pix_add_x < pix_add_y:
            pix_add_y = 0
        elif pix_add_x > pix_add_y:
            pix_add_x = 0
    
    #width greater than max_width, but length smaller, just add to height
    if pix_add_x < 0 and pix_add_y >= 0: 
        pix_add_y = int(round(img_width * ppi_y / ppi_x) - img_height)
        pix_add_x = 0

    #height greater than max_height, but width smaller, just add to width
    if pix_add_y < 0 and pix_add_x >= 0:
        ratio_y = img_height/ppi_y - 1
        pix_add_x  = int(round((ppi_x * ratio_y + ppi_x) - img_width))
        pix_add_y = 0
        #print (ratio_y,ppi_x, ppi_y, round(ppi_x * ratio_y + ppi_x), img_height)

    return dpi_predicted,pix_add_x, pix_add_y

def pixels_calculated(img_height, img_width):
    dpi_predicted=get_dpi_resolution(img_width, img_height)
    
    img_width_inch = img_width / dpi_predicted
    img_height_inch = img_height / dpi_predicted
    #print(img_width_inch, img_height_inch)
    
    pix_add_x = int(round((max_width - img_width_inch) * dpi_predicted))
    pix_add_y = int(round((max_height - img_height_inch) * dpi_predicted))
    return dpi_predicted,pix_add_x, pix_add_y

def pixels_for_ratio(img_height, img_width):
    dpi_predicted=standard_based_dpi(img_height, img_width)

    ppi_x = int(round(max_width * dpi_predicted))
    ppi_y = int(round(max_height * dpi_predicted))

    # calculate pixels to add to maintain aspect ratio for x and y
    if ppi_y != 0:
      pix_add_x  = int(round(ppi_x * img_height/ppi_y) - img_width)
    else:
      print (f'ppi_y is 0, dpi_predicted: {dpi_predicted}, height: {img_height}, width: {img_width}')
    if ppi_x != 0:  
      pix_add_y = int(round(img_width * ppi_y / ppi_x) - img_height)
    else:
      print (f'ppi_x is 0, dpi_predicted: {dpi_predicted}, height: {img_height}, width: {img_width}')
      

    if pix_add_x > 0:
      pix_add_y = 0
    elif pix_add_y > 0:
        pix_add_x = 0
        
    return dpi_predicted, pix_add_x, pix_add_y
    
# add borers to all images in source directory and save them to dest directory  
def add_borders(source_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    i=1
    img_dpis = {}
    for source_filename in sorted(source_dir.glob('*.JPG')):
        s_image = str(source_filename)
        img = Image.open(s_image) # change to CV2
        img_width, img_height = img.size
        #try to aproximate from standard sizes 
        dpi_predicted, pix_add_x, pix_add_y = pixels_for_ratio(img_height, img_width)
        
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

# add borers to all images in source directory and save them to dest directory
#*******************************************************************************
# corrected to address differences in sizes between labels and instances
# dimensions
#*******************************************************************************
def add_borders2(source_dir, dest_dir):
    print("start:  " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    dest_dir.mkdir(parents=True, exist_ok=True)
    i=1
    img_dpis = {}
    for source_filename in sorted(source_dir.glob('*')):
        s_image = str(source_filename)
        img = cv2.imread(s_image) # change to CV2
        img_height, img_width, _ = img.shape
        #try to aproximate from standard sizes 
        dpi_predicted, pix_add_x, pix_add_y = pixels_for_ratio(img_height, img_width)
        
        print (i, source_filename.name,img_width, img_height, dpi_predicted, pix_add_x, pix_add_y)
        img_dpis[source_filename.name] = (i, source_filename.name,img_width, img_height, dpi_predicted, pix_add_x, pix_add_y)
        i=i+1

        # add pixels to original image as black border
        resized_img= cv2.copyMakeBorder(img,0,pix_add_y,0,pix_add_x,cv2.BORDER_CONSTANT,value=0)
        if ("JPG" in source_filename.name):
          cv2.imwrite(str(Path(dest_dir,source_filename.name)), resized_img, params_jpg)
        elif ("png" in source_filename.name):
          cv2.imwrite(str(Path(dest_dir,source_filename.name)), resized_img, params_png)
    print(img_dpis)
    print("end:  " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))


# shrink images to the specified dpi width and height
def shrink_images(source_dir, dest_dir, width_to, height_to):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filepath in sorted(source_dir.glob('*')):
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
            res = cv2.resize(img,None,fx=shrk_factor, fy=shrk_factor, interpolation = cv2.INTER_NEAREST)
            # crop image
            if "JPG" in filepath.name:
                cv2.imwrite(str(Path(dest_dir,filepath.name)),res,params_jpg)
            elif "png" in filepath.name:
                cv2.imwrite(str(Path(dest_dir,filepath.name)),res,params_png)

def pixel_sizes(directory, width_to, height_to ):
    # verify pixel dimensions
    for filepath in sorted(directory.glob('*')):
        s_filepath = str(filepath)
        img = Image.open(str(s_filepath)) #change to cv2
        width,height = img.size
        if height!=height_to or width != width_to:
            print("out of range", filepath.name, height, width)
            #need to crop extra pixels
            if width > width_to:
                print("need to crop width")
            elif height > height_to:
                print("need to crop height")
            crop_images(filepath, width_to, height_to)
                
def crop_images(filepath, width_to, height_to):
    print("cropping to",width_to, height_to)
    #read the image
    img = cv2.imread(str(filepath), cv2.IMREAD_COLOR)
    crop_img = img[0:height_to, 0:width_to]
    if "JPG" in filepath.name:
        cv2.imwrite(str(filepath),crop_img,params_jpg)
    elif "png" in filepath.name:
        cv2.imwrite(str(filepath),crop_img,params_png)
    
    
def get_unique_colours(img):
    aimg= numpy.asarray(img)
    return set( tuple(v) for m2d in aimg for v in m2d )

def get_unique_colours_2(img):
    aimg= numpy.asarray(img)
    return numpy.unique(aimg.reshape(-1, aimg.shape[2]), axis=0)

def get_colour_count(img):
    aimg= numpy.asarray(img)
    return Counter([tuple(colours) for i in aimg for colours in i])

# PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
def getcolourlist(img):
    rgb_img = img.convert('RGB') # create the pixel map
    colourlist={}
    for i in range(img.size[0]):    # for every col:
        for j in range(img.size[1]):    # For every row
            r, g, b = rgb_img.getpixel((i,j)) # set the colour accordingly
            colour=str(r)+","+str(g)+","+str(b)
            if colour in colourlist:
                colourlist[colour]+=1
            else:
                colourlist[colour]=1
    return colourlist

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
            colour = img2[i,j]
            if colour[0] < 100:
                colour[0] = 0
            else:
                colour[0] = 255
            if colour[1] < 100:
                colour[1] = 0
            else:
                colour[1] = 255
            if colour[2] < 100:
                colour[2] = 0
            else:
                colour[2] = 255
            img2[i,j] = colour
    cv2.imwrite(str(filename_labels),img2)

def correct_close_colours(filename_labels, colour_list):
  # test changing colours to nearest match
  img_labels = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
  img2 = img_labels
  for colour in colour_list:
    if colour not in [(255, 255, 0), (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)]:
      #swhitch to find closest match
      # white  (255,255,255)
      # yellow (255,255,  0)
      # blue   (255,  0,  0)
      # red    (  0,  0,255)
      replace_colour = [0,0,0]
      if colour[0] == colour[1] == 0:
          # colour close to red, replace
          replace_colour = [0,0,255]  
      elif colour[1] == colour[2] == 0:
          # colour close to blue, replace
          replace_colour = [255,0,0]
      elif colour[0] != 0 and colour[1] != 0 and colour[2] == 0:
          # colour close to yellow, replace
          replace_colour = [255,255,0]
      elif colour[0] != 0 and colour[1] != 0 and colour[2] != 0:
          # colour close to white, replace
          replace_colour = [255,255,255]
      colour = list(colour)
      if not numpy.array_equal(replace_colour, [0,0,0]):
          replace_colour = numpy.array(replace_colour)
          img2 = replace_colour_in_image(img2,colour,replace_colour)
  print(str(filename_labels))
  cv2.imwrite(str(filename_labels),img2)

def correct_close_colours2(filename_labels):
    # make all colours either black, white, red or yellow
    # turning any colour channel with less than 100 will to 0
    img_labels = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    height,width,channels = img_labels.shape
    img2 = img_labels
    for i in range(height):
        for j in range(width):
            colour = img2[i,j]
###################################################
            replace_colour = [0,0,0]
            if colour[0] == colour[1] == 0 and colour[2] != 0:
                # colour close to red, replace
                replace_colour = [0,0,255]  
            elif colour[0] != 0 and colour[1] == colour[2] == 0:
                # colour close to blue, replace
                replace_colour = [255,0,0]
            elif colour[0] != 0 and colour[1] != 0 and colour[2] == 0:
                # colour close to yellow, replace
                replace_colour = [255,255,0]
            elif colour[0] != 0 and colour[1] != 0 and colour[2] != 0:
                # colour close to white, replace
                replace_colour = [255,255,255]
###################################################
            img2[i,j] = replace_colour
    cv2.imwrite(str(filename_labels),img2)

def correct_close_colours3(filename_labels, colour_list):
    # make all colours either black, white, red or yellow
    # turning any colour channel with less than 100 will to 0
    img_labels = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    height,width,channels = img_labels.shape
    # !!!!!!!!!!Colurs are reversed BRG not RGB!!!!!!!!!!!!
    # openCV cv2.imread() loads images as BGR while numpy.imread() loads them as RGB.
    for colour in colour_list:
      colour = colour[::-1]
      # change list to BGR: yellow = (0, 255, 255), red = (0,0,255), blue = (255,0,0)
      if colour not in [(0, 255, 255), (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)]:
        replace_colour = [0,0,0]
        if colour[0] == colour[1] == 0 and colour[2] != 0:
            # colour close to red, replace
            replace_colour = [0,0,255]  
        elif colour[0] != 0 and colour[1] == colour[2] == 0:
            # colour close to blue, replace
            replace_colour = [255,0,0]
        elif colour[0] == 0 and colour[1] != 0 and colour[2] != 0:
            # colour close to yellow, replace
            replace_colour = [0,255,255]
        elif colour[0] != 0 and colour[1] != 0 and colour[2] != 0:
            # colour close to white, replace
            replace_colour = [255,255,255]
        #print(list(colour))
        pxlist = getobject(img_labels,list(colour))
        #print(pxlist[0])
        for px_xy in pxlist:
          #print(px_xy)
          img_labels[px_xy[0],px_xy[1]] = replace_colour
    cv2.imwrite(str(filename_labels),img_labels)

def correct_close_colours4(filename_labels, colour_list):
    # make all colours either black, white, red or yellow
    # turning any colour channel with less than 100 will to 0
    img_labels = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    height,width,channels = img_labels.shape
    # !!!!!!!!!!Colurs are reversed BRG not RGB!!!!!!!!!!!!
    # openCV cv2.imread() loads images as BGR while numpy.imread() loads them as RGB.
    for colour in colour_list:
      colour = colour[::-1]
      # change list to BGR: yellow = (0, 255, 255), red = (0,0,255), blue = (255,0,0)
      if colour not in [(0, 255, 255), (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)]:
        replace_colour = [0,0,0]
        if colour[0] == colour[1] == 0 and colour[2] != 0:
            # colour close to red, replace
            replace_colour = [0,0,255]  
        elif colour[0] != 0 and colour[1] == colour[2] == 0:
            # colour close to blue, replace
            replace_colour = [255,0,0]
        elif colour[0] == 0 and colour[1] != 0 and colour[2] != 0:
            # colour close to yellow, replace
            replace_colour = [0,255,255]
        elif colour[0] != 0 and colour[1] != 0 and colour[2] != 0:
            # colour close to white, replace
            replace_colour = [255,255,255]
        img_labels = replace_colour_in_image(img_labels,colour,replace_colour)
    cv2.imwrite(str(filename_labels),img_labels)

def verify_label_colours(source_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    print("start:  " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    #copy all files to dest_dir
    for filepath in sorted(source_dir.glob('*')):
         shutil.copy(str(filepath), Path(dest_dir, filepath.name))
                                
    for dest_filename in sorted(dest_dir.glob('*labels.png')):
        s_filename = str(dest_filename)
        img = Image.open(str(s_filename)) # change to cv2
        colours = get_colour_count(img)        
        colourlist=[*colours]
        incorrect_label_colour = 0
        for colour in colourlist:
            if colour not in [(255, 255, 0), (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)]:
                incorrect_label_colour = 1
                break
        if len(colours)>5 or incorrect_label_colour == 1:
            print(dest_filename.name, len(colours), "needs correcting colours",sorted(colourlist))
            # correct close matching colours on border
            correct_close_colours4(dest_filename, colourlist)
            correct_label_colours(dest_filename)
        else:
            print(dest_filename.name, len(colours), "ok",sorted(colourlist))
    print("finish: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

# change colours with counts smaller than 500 to the background colour
def correct_instance_colours(filename_labels):
    img_instances = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    height,width,channels = img_instances.shape

    colourlist=get_colour_count(img_instances)
    #print("initial colour count", len(colourlist))
    #print(colourlist)
    bigcolours ={}
    countuniques = 0
    for colour in colourlist:
        if colourlist[colour] < 500:
            countuniques += 1
        else:
            bigcolours[colour]=colourlist[colour]
    img2 = img_instances
    background = (0, 0, 0)
    for i in range(height):
        for j in range (width):
            colour = img2[i,j]
            if not (tuple(colour) in bigcolours):
                img2[i,j] = background
    cv2.imwrite(str(filename_labels),img2)

#make all instance backgrounds solid black
def correct_instance_backgrounds(filename_labels):
    img_instances = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    height,width,channels = img_instances.shape

    colourlist=get_unique_colours(img_instances)
    corrections = False
    corrections_list = []
    #first check if there are colours close to black in the image
    for colour in colourlist:
        if colour[0] < 50 and colour[1] < 50 and colour[2] < 50 and \
           colour != (0,0,0):
            corrections_list.append(list(colour))
            corrections = True
    # if there are colours close to black, get a list of corresponding pixels
    # and correct them (make them black)
    if corrections:
        background = (0, 0, 0)
        for colour_match in corrections_list:
            img2 = img_instances
            # numpy where and all help in selecting only matching colour pixels
            indices = numpy.where(numpy.all(img2 == colour_match, axis=-1))
            coordinates = list(zip(indices[0], indices[1]))
            for i, j in coordinates:
               img2[i,j] = background 
        print("correcting:", filename_labels.name)
        cv2.imwrite(str(filename_labels),img2,params_png)
    else:
        print(filename_labels.name, "OK")

# make instance sizes equal to sizes of labels
def compare_instances_to_labels(filename_labels):
    img_instances = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    img_labels = cv2.imread(str(filename_labels).replace("instances","labels"), cv2.IMREAD_COLOR)
    
    height,width,channels = img_instances.shape

    colorlist=get_colour_count(img_instances)
    #print("initial colour count", len(colourlist))
    #print(colourlist)
    bigcolours ={}
    countuniques = 0
    for colour in colourlist:
        if colourlist[colour] < 500:
            countuniques += 1
        else:
            bigcolours[colour]=colourlist[colour]
    img2 = img_instances
    background = (0, 0, 0)
    for i in range(height):
        for j in range (width):
            colour = img2[i,j]
            if not (tuple(colour) in bigcolours):
                img2[i,j] = background
    cv2.imwrite(str(filename_labels),img2)
    
def verify_instance_borders(dest_dir):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for dest_filename in sorted(dest_dir.glob('*instances.png')):
        s_filename = str(dest_filename)
        img = Image.open(str(s_filename)) # change to CV2
        colours = get_colour_count(img)
        if len(colours)>20:
            print(dest_filename.name, len(colours), "needs correcting colours")
            correct_instance_colours(dest_filename)
        else:
            print(dest_filename.name, len(colours), "ok")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

def verify_instance_backgrounds(dest_dir):
    print("start:  " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for dest_filename in sorted(dest_dir.glob('*instances.png')):
        s_filename = str(dest_filename)
        img = Image.open(str(s_filename)) # change to CV2
        correct_instance_backgrounds(dest_filename)
    print("finish: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

def verify_instance_labels_match(dest_dir):
    print("start:  " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for instance_file in sorted(dest_dir.glob('*instances.png')):
        img_instance = cv2.imread(str(instance_file), cv2.IMREAD_COLOR)
        label_file = Path(dest_dir,instance_file.name.replace("instances","labels"))
        img_labels = cv2.imread(str(label_file), cv2.IMREAD_COLOR)
        bkgs_ok, len_bkg_ins, len_bkg_lbl = instance_labels_match(img_instance,[0,0,0],img_labels,[0,0,0])
        if not bkgs_ok:
            print("Dif:", instance_file.name,"(",len_bkg_ins,")" , \
                  label_file.name, "(", len_bkg_lbl, ")" )
            create_labels_from_instances(instance_file,img_instance,img_labels)
        elif bkgs_ok:
            print("OK:in",instance_file.name, "(",len_bkg_ins,")" , \
                  label_file.name, "(", len_bkg_lbl, ")" )
    print("finish: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

def instance_labels_match(img_instance,ins_bkg,img_labels,lbl_bkg):
    #print(img_instance,ins_bkg)
    instance_bkg = getobject(img_instance,ins_bkg)
    #print(img_labels,lbl_bkg)
    label_bkg = getobject(img_labels,lbl_bkg)
    bkg_ok = False
    if len(instance_bkg) != len(label_bkg):
        bkg_ok = False
    else:
        bkg_ok = True
    return bkg_ok, len(instance_bkg), len(label_bkg)
    
#get all pixel coordinates for a given colour
def getobject(img,colour):
    indices = numpy.where(numpy.all(numpy.array(img) == colour, axis=-1))
    pixels = list(zip(indices[0], indices[1]))
    return pixels

#get all contour pixels from a blob
def getcontour(pixels):
  contour=[]
  pixels = set(pixels)
  for pixel in pixels:
    # if any of the eight adjacent pixels is not in the pixel set
    # then the pixel sits in the shape border
    if not (pixel[0]-1,pixel[1]-1) in pixels:
      contour.append(pixel)    
    elif not (pixel[0],pixel[1]-1) in pixels:
      contour.append(pixel)
    elif not (pixel[0]+1,pixel[1]-1) in pixels:
      contour.append(pixel)
    elif not (pixel[0]-1,pixel[1]) in pixels:
      contour.append(pixel)
    elif not (pixel[0]+1,pixel[1]) in pixels:
      contour.append(pixel)
    elif not (pixel[0]-1,pixel[1]+1) in pixels:
      contour.append(pixel)
    elif not (pixel[0],pixel[1]+1) in pixels:
      contour.append(pixel)
    elif not (pixel[0]+1,pixel[1]+1) in pixels:
      contour.append(pixel)
  return contour

# correct using pil for fast pixel by pixel 
def correct_instance_contours(instance_file,img_instance,img_labels):
    width, height = img_instance.size
    # get all shapes in the instances image
    colours = get_unique_colours_2(img_instance)
    colours = colours.tolist()
    colours.remove([0,0,0])
    bkgs_match = False
    while not bkgs_match:
        # for each shape
        for shape_colour in colours:
            shape_pixels = getobject(img_instance, shape_colour)
        # get shape contour
            shape_contour = getcontour(shape_pixels)
        # use contour in labels image to verify if external adjacent are background
        # if not background in labels, change to current shape colour in instances
            for pixel in shape_contour:
                adjacent_pixels = getadjacentpixels(pixel, height, width)
                for adjpix in adjacent_pixels:
                    x = int(adjpix[1]) # column
                    y = int(adjpix[0]) # row
                    colour_in_lbl = img_labels.getpixel((x,y))
                    if not numpy.array_equal(colour_in_lbl, [0,0,0]):
                        img_instance.putpixel((x,y),tuple(shape_colour))
        # if backgronds match stop else repeat for all shapes
        bkgs_match = instance_labels_match(img_instance,(0,0,0),img_labels,(0,0,0))     
        # save new instances file
        cv2.imwrite(str(instance_file),numpy.array(img_instance),params_png)

# using CV2, use instances to generate labels
def create_labels_from_instances(instance_file,img_instance,img_labels):
    height,width,channels = img_instance.shape
    # get all shapes in the instances image
    colours = get_unique_colours_2(img_instance)
    colours = colours.tolist()
    colours.remove([0,0,0])
    # for each shape
    for shape_colour in colours:
        shape_pixels = getobject(img_instance, shape_colour)
    # get shape contour
        shape_contour = getcontour(shape_pixels)
        # get contour centre coordinates
        centre_pixel = getcontourcentre(shape_contour)
        # get the colour for centre pixel from labels
        x = int(centre_pixel[1]) # column
        y = int(centre_pixel[0]) # row
        colour_in_lbl = img_labels[y,x]
        # if the colour in the centre is not black replace
        # replace shape colour with centre colour
        if not numpy.array_equal(colour_in_lbl, [0,0,0]):
            #img_instance =
            print("clfi swapping colours", shape_colour, " for ", colour_in_lbl )
            img_instance = replace_colour_in_image(img_instance, shape_colour, colour_in_lbl)
            #img_instance[numpy.where((img_instance == shape_colour).all(axis = 2))] = colour_in_lbl
    cv2.imwrite(str(instance_file).replace("instances","labels"),img_instance,params_png)

# image: source image to replace
# colour: colour to replace as a list
# replace_colour: new colour as numpy array
def replace_colour_in_image(image,colour,replace_colour):
    image[numpy.where((image == colour).all(axis = 2))] = replace_colour
    #print("replace ", colour, " with ", replace_colour)
    return image
    
def getadjacentpixels(pixel, height, width):
    # pixel coordinates are in the form: (row, column)
    # min for both is 0
    # max for row is height - 1
    # max for column is width - 1
    adjacent = []
    if pixel[0]-1 >= 0:
        adjacent.append((pixel[0]-1, pixel[1]))
    if pixel[0]-1 >= 0 and pixel[1]+1 < width:
        adjacent.append((pixel[0]-1,pixel[1]+1))
    if pixel[0]-1 >=0 and pixel[1]-1 >= 0:
        adjacent.append((pixel[0]-1,pixel[1]-1))
    if pixel[1]-1 >= 0:
        adjacent.append((pixel[0],pixel[1]-1))
    if pixel[0]+1 < height and pixel[1]-1 >= 0:
        adjacent.append((pixel[0]+1,pixel[1]-1))
    if pixel[0]+1 < height:
        adjacent.append((pixel[0]+1,pixel[1]))
    if pixel[1]+1 < width:
        adjacent.append((pixel[0],pixel[1]+1))
    if pixel[0]+1 < height and pixel[1]+1 < width:
        adjacent.append((pixel[0]+1,pixel[1]+1))
    return adjacent

def getcontourcentre(shape_contour):
    min_x = min_y = max_x = max_y = 0
    for pair in shape_contour:
        if min_x==min_y==max_y==max_x==0:
            min_y, min_x = pair
            max_y, max_x = pair
        else:
            if pair[0] < min_y:
                min_y = pair[0]
            if pair[1] < min_x:
                min_x = pair[1]
            if pair[0] > max_y:
                max_y = pair[0]
            if pair[1] > max_x:
                max_x = pair[1]
    mid_y = int(round(min_y + (max_y-min_y)/2))
    mid_x = int(round(min_x + (max_x-min_x)/2))
    return (mid_y, mid_x)

def getcontourcorners(shape_contour):
    min_x = min_y = max_x = max_y = 0
    for pair in shape_contour:
        if min_x==min_y==max_y==max_x==0:
            min_y, min_x = pair
            max_y, max_x = pair
        else:
            if pair[0] < min_y:
                min_y = pair[0]
            if pair[1] < min_x:
                min_x = pair[1]
            if pair[0] > max_y:
                max_y = pair[0]
            if pair[1] > max_x:
                max_x = pair[1]
    mid_y = int(round(min_y + (max_y-min_y)/2))
    mid_x = int(round(min_x + (max_x-min_x)/2))
    return ((min_y, min_x), (max_y, max_x))

def correct_instance_colours(filename_labels):
    img_instances = cv2.imread(str(filename_labels), cv2.IMREAD_COLOR)
    height,width,channels = img_instances.shape

    colourlist=get_colour_count(img_instances)
    #print("initial colour count", len(colourlist))
    #print(colourlist)
    bigcolours ={}
    countuniques = 0
    for colour in colourlist:
        if colourlist[colour] < 500:
            countuniques += 1
        else:
            bigcolours[colour]=colourlist[colour]
    img2 = img_instances
    background = (0, 0, 0)
    for i in range(height):
        for j in range (width):
            colour = img2[i,j]
            if not (tuple(colour) in bigcolours):
                img2[i,j] = background
    cv2.imwrite(str(filename_labels),img2)    

#rename files:
# *.jpeg and *.jpg as *.JPG
# *_all.png as _instances.png
# *_sel.png as _labels.png
def rename_files(source_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filepath in sorted(source_dir.glob('*')):
        if filepath.is_file():
            workfile = filepath.name
            if ".jpg" in workfile:
                workfile = workfile.replace(".jpg",".JPG")
            elif ".jpeg" in workfile:
                workfile = workfile.replace(".jpeg",".JPG")
            elif "_all.png" in workfile:
                workfile = workfile.replace("_all.png","_instances.png")
            elif "_sel.png" in filepath.name:
                workfile = workfile.replace("_sel.png","_labels.png")
            workfile = workfile.replace(" ","_") #remove spaces from names
            workfile = workfile.replace("__","_") #remove double underscores from names
            #print(workfile)
            shutil.copy(str(filepath), Path(dest_dir, workfile))

def rezise_png_images(source_dir):
    for source_filename in source_dir.iterdir():
        #read the image
        if ".png" in source_filename.name:
            img = cv2.imread(str(source_filename), cv2.IMREAD_COLOR)
            params = list()
            params.append(cv2.IMWRITE_PNG_COMPRESSION)
            params.append(9)
            cv2.imwrite(str(source_filename),img,params)

def list_image_size(source_dir):
    print("start:  " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for source_filename in source_dir.iterdir():
        #read the image
        if ".png" in source_filename.name or ".JPG"  in source_filename.name:
            img = cv2.imread(str(source_filename), cv2.IMREAD_COLOR)
            height,width,channels = img.shape
            print(source_filename.name,":",height,":",width,":",channels, ":")
    print("finish: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

def get_original_filename(instance_file, source_dir):
    workfile = instance_file.name.replace("_instances.png","")
    workfile = workfile.replace("_","*")
    instance_file = source_dir.glob("*"+workfile+".*")
    return list(instance_file)[0]
    
# using CV2, use instances to generate labels
def extract_segments(image_file,img_instance,img_labels,size):
    height,width,channels = img_instance.shape
    # get all shapes in the instances image
    colours = get_unique_colours_2(img_instance)
    colours = colours.tolist()
    if [0,0,0] in colours:
        colours.remove([0,0,0])
    else:
        print("Background is not black")
        # get it as  the colour at 0,0
        the_background = list(img_instance[0,0])
        print(the_background)
        colours.remove(the_background)
    lbls_i = 1
    bcds_i = 1
    colc_i = 1
    bkgs_match = False
    # for each shape
    for shape_colour in colours:
        shape_pixels = getobject(img_instance, shape_colour)
    # get shape contour
        shape_contour = getcontour(shape_pixels)
        # get contour centre coordinates
        centre_pixel = getcontourcentre(shape_contour)
        # get the colour for centre pixel from labels
        x = int(centre_pixel[1]) # column
        y = int(centre_pixel[0]) # row
        colour_in_lbl = img_labels[y,x]
        #open the original file
        full_image = cv2.imread(str(image_file))
        #recalculate pixels added to width
        img_height,img_width,_ = full_image.shape
        _, pix_add_x, _ = pixels_for_ratio(img_height, img_width)
        width_calc = img_width + pix_add_x
        # get contour corners
        corner_pixels = getcontourcorners(shape_contour)
        # transform corner coordinates to resolution of the original image
        if size == 96:
            x1 = int(corner_pixels[0][1]*width_calc/max_width_96) # column
            y1 = int(corner_pixels[0][0]*width_calc/max_width_96) # row
            x2 = int(corner_pixels[1][1]*width_calc/max_width_96) # column
            y2 = int(corner_pixels[1][0]*width_calc/max_width_96) # row
        elif size == 0: # no need to transform coordinates
            x1 = int(corner_pixels[0][1]) # column
            y1 = int(corner_pixels[0][0]) # row
            x2 = int(corner_pixels[1][1]) # column
            y2 = int(corner_pixels[1][0]) # row
        
        #get the segment from the full image
        segment = full_image[y1:y2, x1:x2]
        suffix = "_"
        # use colour in centre to get segment type
        # if red save segment as label
        if numpy.array_equal(colour_in_lbl, [0,0,255]):
            suffix += "lbl"+'{:02d}'.format(lbls_i)
            lbls_i+=1
        # if yellow save segment as colour chart
        elif numpy.array_equal(colour_in_lbl, [0,255,255]):
            suffix += "clc"+'{:02d}'.format(colc_i)
            colc_i+=1
        # if white save segment as barcode
        elif numpy.array_equal(colour_in_lbl, [255,255,255]):
            suffix += "bcd"+'{:02d}'.format(bcds_i)
            bcds_i+=1
        cv2.imwrite(str(image_file).replace(".JPG",suffix+".jpg"),segment,params_jpg)

def extract_segments_from_files(instances_dir, full_image_dir):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for instance_file in sorted(instances_dir.glob('*instances.png')):
        img_instance = cv2.imread(str(instance_file), cv2.IMREAD_COLOR)
        label_file = Path(instances_dir,instance_file.name.replace("instances","labels"))
        img_labels = cv2.imread(str(label_file), cv2.IMREAD_COLOR)
        image_file = get_original_filename(instance_file, full_image_dir)
        extract_segments(image_file,img_instance,img_labels,96)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    
def extract_segments_from_gt(images_dir):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for instance_file in sorted(images_dir.glob('*instances.png')):
        img_instance = cv2.imread(str(instance_file), cv2.IMREAD_COLOR)
        label_file = Path(images_dir,instance_file.name.replace("instances","labels"))
        img_labels = cv2.imread(str(label_file), cv2.IMREAD_COLOR)
        image_file = Path(images_dir,instance_file.name.replace("_instances.png",".JPG"))
        print(instance_file,"\n",label_file,"\n",image_file)
        extract_segments(image_file,img_instance,img_labels,0)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
# background colours: light blue, pink, light yellow
bkg_colours = [[227,206,166],[153,154,251],[153,255,255]]

def change_instance_bkg(source_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for filepath in sorted(source_dir.glob('*')):
        s_filename = str(filepath)
        if "instances" in s_filename:
            img_instance = cv2.imread(s_filename, cv2.IMREAD_COLOR)
            colours = get_unique_colours_2(img_instance)
            colours = colours.tolist()
            #print(colours)
            for bkg_c in bkg_colours:
                #print (bkg_c)
                if not(bkg_c in colours):
                    img_instance[numpy.where((img_instance == [0,0,0]).all(axis = 2))] = bkg_c
                    break
            cv2.imwrite(str(Path(dest_dir,filepath.name)),img_instance)
        else:
            shutil.copy(s_filename, Path(dest_dir, filepath.name))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    
