#
# Preprocessing and verification before training
#

from pathlib import Path
from  processgti.herbariumgtiv import *
from matplotlib import pyplot as plt

# Directory containing the original set of segmented images
source_dir = Path(Path().absolute().parent, "herbariumsheets","sample05b")
# Directory containing the segments (rezised to 96DPI)
finished_dir = Path(Path().absolute().parent, "herbariumsheets","sample05b", "finalpass")


sample_file = Path(source_dir, "B 10 0003200_clc01.jpg")

# Smooth (blur) image by applying an averaging filter
img = cv2.imread(str(sample_file))
##kernel = numpy.ones((5,5),numpy.float32)/25
##dst = cv2.filter2D(img,-1,kernel)
##
##plt.subplot(121),plt.imshow(img),plt.title('Original')
##plt.xticks([]), plt.yticks([])
##plt.subplot(122),plt.imshow(dst),plt.title('Averaging')
##plt.xticks([]), plt.yticks([])
##plt.show()
##
### Blur: the same efect as above is achieved with the blur function
##blur = cv2.blur(img,(5,5))
## 
##plt.subplot(121),plt.imshow(img),plt.title('Original')
##plt.xticks([]), plt.yticks([])
##plt.subplot(122),plt.imshow(blur),plt.title('Blurred')
##plt.xticks([]), plt.yticks([])
##plt.show()
##
### Gausian Blur: alternative to box kernel, effective for removing gaussian noise
##blur = cv2.GaussianBlur(img,(5,5),0)
##
##plt.subplot(121),plt.imshow(img),plt.title('Original')
##plt.xticks([]), plt.yticks([])
##plt.subplot(122),plt.imshow(blur),plt.title('Gaussian Blur')
##plt.xticks([]), plt.yticks([])
##plt.show()
##
### Median Blur: alternative to box kernel and gaussian, effective for reducing noise
##median = cv2.medianBlur(img,5)
##
##plt.subplot(121),plt.imshow(img),plt.title('Original')
##plt.xticks([]), plt.yticks([])
##plt.subplot(122),plt.imshow(median),plt.title('Median Blur')
##plt.xticks([]), plt.yticks([])
##plt.show()
##
### Change contrast and brightnedd of an image
### make image brighter
##new_image = numpy.zeros(img.shape, img.dtype)
##
##alpha = 1.0 # Simple contrast control
##beta = 50    # Simple brightness control
##
##new_image = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
##
##plt.subplot(121),plt.imshow(img),plt.title('Original')
##plt.xticks([]), plt.yticks([])
##plt.subplot(122),plt.imshow(new_image),plt.title('Brighter')
##plt.xticks([]), plt.yticks([])
##plt.show()
##
##
### make image darker
##new_image = numpy.zeros(img.shape, img.dtype)
##
##alpha = 1.0 # Simple contrast control
##beta = -50    # Simple brightness control
##
##new_image = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
##
##plt.subplot(121),plt.imshow(img),plt.title('Original')
##plt.xticks([]), plt.yticks([])
##plt.subplot(122),plt.imshow(new_image),plt.title('Darker')
##plt.xticks([]), plt.yticks([])
plt.show()

# add noise
m = (20,20,20) 
s = (20,20,20)
noise = numpy.zeros(img.shape, img.dtype)
buff = img.copy()
cv2.randn(noise,m,s)
buff=cv2.add(buff, noise, dtype=cv2.CV_8UC3) 

plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(buff),plt.title('noisy')
plt.xticks([]), plt.yticks([])
plt.show()