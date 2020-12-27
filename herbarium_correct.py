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
    # get the shape of the colourchart
    shape_colourchart = getobject(img_labels, yellow_mask)
    # get the shape of the scale
    shape_scale = getobject(img_labels, blue_mask)
    # turn scale into colourchart
    for img_point in shape_scale:
        img_labels[img_point[0],img_point[1]]=yellow_mask
    # get the colour of the colourchart in instances
    colchrt_contour = getcontour(shape_colourchart)
    centre_pixel = getcontourcentre(colchrt_contour)    
    # get the colour for centre pixel from instances
    x = int(centre_pixel[1]) # column
    y = int(centre_pixel[0]) # row
    colour_in_ins = img_instance[y,x]
    cc_corner_pixels = getcontourcorners(colchrt_contour)
    # get the contour of the scale 
    scale_contour = getcontour(shape_scale)
    sc_corner_pixels = getcontourcorners(scale_contour)
    # turn scale into colourchart
    for img_point in shape_scale:
        img_labels[img_point[0],img_point[1]]=yellow_mask
    for img_point in shape_scale:
        img_instance[img_point[0],img_point[1]]=colour_in_ins
    for img_point in shape_colourchart:
        img_instance[img_point[0],img_point[1]]=colour_in_ins

    for y in range(sc_corner_pixels[0][0],cc_corner_pixels[1][0]-1):
        for x in range(0,sc_corner_pixels[0][1]+1):
            img_labels[y,x]=red_mask
            img_instance[y,x]=blue_mask
            
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
source_dir = Path(Path().absolute().parent, "herbariumsheets","AMDCorrect")
# Directory containing corrected images
corrected_dir = Path(Path().absolute().parent, "herbariumsheets","AMDCorrect", "corrected")

correct_amd_gts(source_dir, corrected_dir)
