import cv2 as cv2
import numpy as np

# parameters for jpg
# required for preserving quality as much as possible after each transformation
params_jpg = list()
params_jpg.append(cv2.IMWRITE_JPEG_QUALITY)
params_jpg.append(94)

from matplotlib import pyplot as plt

from pathlib import Path

def image_crop(x, crop_size=(256,256)):
    #get image height and width
    h, w, _ = x.shape
    #get the ranges for the random generator
    rangew = (w - crop_size[0]) // 2 if w>crop_size[0] else 0
    rangeh = (h - crop_size[1]) // 2 if h>crop_size[1] else 0
       
    offsetw = 0 if rangew == 0 else np.random.randint(rangew)
    offseth = 0 if rangeh == 0 else np.random.randint(rangeh)
    
    cropped_x = x[offseth:offseth+crop_size[1], offsetw:offsetw+crop_size[0], :]
    if cropped_x.shape[-1] == 0:
        return x
    else:
        return cropped_x

def crop_images(source_dir, dest_dir, c_height,c_width):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for source_filename in source_dir.iterdir():
        if ".JPG"  in source_filename.name:

            img1 = cv2.imread(str(source_filename), cv2.IMREAD_COLOR)
            #resize, flip and crop
            resized_i = cv2.resize(img1,None,fx=0.6, fy=0.6, interpolation = cv2.INTER_NEAREST)

            flip_img = cv2.flip(resized_i, -1 )

            crop_flip = image_crop(flip_img,crop_size=(c_width,c_height))

            cv2.imwrite(str(Path(dest_dir,source_filename.name.replace(".JPG","_crpf.JPG"))),crop_flip,params_jpg)



source_dir = Path(Path().absolute().parent, "slides","kewgt500")
dest_dir = Path(Path().absolute().parent, "slides","kewgt500","cropped")
c_height = 300
c_width  = 800
crop_images(source_dir, dest_dir, c_height,c_width)


