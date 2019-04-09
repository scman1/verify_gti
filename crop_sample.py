import cv2 as cv2
import numpy as np

# parameters for jpg
# required for preserving quality as much as possible after each transformation
params_jpg = list()
params_jpg.append(cv2.IMWRITE_JPEG_QUALITY)
params_jpg.append(94)

from matplotlib import pyplot as plt

from pathlib import Path

def random_crop(x, y, crop_size=(256,256)):
    assert x.shape[0] == y.shape[0]
    assert x.shape[1] == y.shape[1]
    h, w, _ = x.shape
    rangew = (w - crop_size[0]) // 2 if w>crop_size[0] else 0
    rangeh = (h - crop_size[1]) // 2 if h>crop_size[1] else 0
    
    offsetw = 0 if rangew == 0 else np.random.randint(rangew)
    offseth = 0 if rangeh == 0 else np.random.randint(rangeh)
    cropped_x = x[offseth:offseth+crop_size[1], offsetw:offsetw+crop_size[0], :]
    cropped_y = y[offseth:offseth+crop_size[1], offsetw:offsetw+crop_size[0], :]
    cropped_y = cropped_y[:, :, ~np.all(cropped_y==0, axis=(0,1))]
    if cropped_y.shape[-1] == 0:
        return x, y
    else:
        return cropped_x, cropped_y
#
def random_crop2(x, crop_size=(256,256)):
    #get image height and width
    h, w, _ = x.shape
    #get the ranges for the random generator
    rangew = (w - crop_size[0]) // 2 if w>crop_size[0] else 0
    rangeh = (h - crop_size[1]) // 2 if h>crop_size[1] else 0
    
    print ("ranges:  ", rangew, rangeh)
    
    offsetw = 0 if rangew == 0 else np.random.randint(rangew)
    offseth = 0 if rangeh == 0 else np.random.randint(rangeh)
    print ("offsets: ", offsetw,offseth)
    
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
            height,width,channels = img1.shape
            print(source_filename.name,":",height,":",width,":",channels, ":")
            # add border and crop
            constant= cv2.copyMakeBorder(img1,100,100,100,100,cv2.BORDER_CONSTANT,value=(0,0,0))

            crop_constant = random_crop2(constant,crop_size=(c_width,c_height))

            #resize and crop
            resized_i = cv2.resize(img1,None,fx=0.6, fy=0.6, interpolation = cv2.INTER_NEAREST)

            crop_resized = random_crop2(resized_i,crop_size=(c_width,c_height))

            #resize, flip and crop

            flip_img = cv2.flip(resized_i, -1 )

            crop_flip = random_crop2(flip_img,crop_size=(c_width,c_height))
            
            plt.subplot(421),plt.imshow(img1,'gray'),plt.title('ORIGINAL')
            plt.subplot(423),plt.imshow(constant,'gray'),plt.title('CONSTANT')
            plt.subplot(424),plt.imshow(crop_constant,'gray'),plt.title('CROP CONSTANT')
            plt.subplot(425),plt.imshow(resized_i,'gray'),plt.title('RESIZED')
            plt.subplot(426),plt.imshow(crop_resized,'gray'),plt.title('CROP RESIZED')
            plt.subplot(427),plt.imshow(flip_img,'gray'),plt.title('FLIPPED')
            plt.subplot(428),plt.imshow(crop_flip,'gray'),plt.title('CROP FLIPPED')
            plt.show()
            cv2.imwrite(str(Path(dest_dir,source_filename.name.replace(".JPG","_crpc.JPG"))),crop_constant,params_jpg)
            cv2.imwrite(str(Path(dest_dir,source_filename.name.replace(".JPG","_crpr.JPG"))),crop_resized,params_jpg)
            cv2.imwrite(str(Path(dest_dir,source_filename.name.replace(".JPG","_crpf.JPG"))),crop_flip,params_jpg)

def list_image_size(source_dir):
    for source_filename in source_dir.iterdir():
        #read the image
        if ".png" in source_filename.name or ".JPG"  in source_filename.name:
            img = cv2.imread(str(source_filename), cv2.IMREAD_COLOR)
            height,width,channels = img.shape
            print(source_filename.name,":",height,":",width,":",channels, ":")

source_dir = Path(Path().absolute().parent, "slides","kewgt500t")
dest_dir = Path(Path().absolute().parent, "slides","kewgt500t","cropped")
c_height = 300
c_width  = 800
crop_images(source_dir, dest_dir, c_height,c_width)


