#
# Preprocessing and verification before training
#

from pathlib import Path
from  processgti.herbariumgtiv import *

# merge scale and colourchart into colourchart for image targets
# - add a red label rectangle for the herbarium name tag
# - use the blue colour as the safe colour for the instance
def correct_gts(image_file,img_instance,img_labels,corrected_dir):
    height,width,channels = img_instance.shape
    yellow_mask = [0,255,255]
    blue_mask = [255,0,0]
    red_mask = [0,0,255]
    pink_mask = [255,0,255]
    olive_mask = [0,130,0]
    # get the shape of the colourchart
    shape_colourchart = getobject(img_instance, yellow_mask)
    # turn colourchart into scale in labels
    for img_point in shape_colourchart:
        img_labels[img_point[0],img_point[1]]=yellow_mask
    # get individuals from fragments on instances 
    # get the shape of the scale
    shape_scale = getobject(img_instance, blue_mask)
    # change colour of second scale in instances
    # the lower coordinates of the cc are under the
    # upper coordinates of the scale
    colchrt_contour = getcontour(shape_colourchart)
    cc_corner_pixels = getcontourcorners(colchrt_contour)
    for img_point in shape_scale:
        if img_point[0] >= cc_corner_pixels[1][0]:
            img_instance[img_point[0],img_point[1]]=pink_mask
    # change colour of first colourchart in instances
    # the lower coordinates of the upper cc are above the
    # upper coordinates of the first scale
    scale_contour = getcontour(shape_scale)
    sc_corner_pixels = getcontourcorners(scale_contour)
    for img_point in shape_colourchart:
        if img_point[0] <= sc_corner_pixels[0][0]:
            img_instance[img_point[0],img_point[1]]=olive_mask

            
    corrected_labels=Path(corrected_dir,image_file.name.replace(".JPG","_labels.png"))
    corrected_instance=Path(corrected_dir,image_file.name.replace(".JPG","_instances.png"))
    cv2.imwrite(str(corrected_labels), img_labels, params_png)
    cv2.imwrite(str(corrected_instance), img_instance, params_png)

def correct_amd_gts(instances_dir, corrected_dir):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for instance_file in sorted(instances_dir.glob('*instances.png')):
        img_instance = cv2.imread(str(instance_file), cv2.IMREAD_COLOR)
        label_file = Path(instances_dir,instance_file.name.replace("instances","labels"))
        image_file = Path(instances_dir,instance_file.name.replace("_instances.png",".JPG"))
        img_labels = cv2.imread(str(label_file), cv2.IMREAD_COLOR)
        correct_gts(image_file,img_instance,img_labels,corrected_dir)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))



# Directory containing the ground truths to correct
source_dir = Path(Path().absolute().parent, "herbariumsheets","helsinkiFix")
# Directory containing corrected images
corrected_dir = Path(Path().absolute().parent, "herbariumsheets","helsinkiFix", "corrected")

correct_amd_gts(source_dir, corrected_dir)
