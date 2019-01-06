#
# Preprocessing and verification before training
#

from pathlib import Path
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
    for filepath in sorted(source_dir.glob('*.jpg')):
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

# Directory containing the original set of segmented images
source_dir = Path(Path().absolute().parent, "herbariumsheets","sample05b","originals")
# Directory containing the segments (rezised to 96DPI)
finished_dir = Path(Path().absolute().parent, "herbariumsheets","sample05b", "modified")

seed_test_set(source_dir, finished_dir)

