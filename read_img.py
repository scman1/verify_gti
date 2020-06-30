import numpy as np
import cv2
import csv
import sys
from datetime import datetime
from processgti.microscopygtiv import *

def mark_instances(img_raw,img_instances):
    ins_colours = get_unique_colours_2(img_instances)
    rectangles = []
    for shape_colour in ins_colours:
        shape_pixels = getobject(img_instances, shape_colour)
        shape_contour = getcontour(shape_pixels)
        centre_pixel = getcontourcentre(shape_contour)
        # get the colour for centre pixel from labels
        x = int(centre_pixel[1]) # column
        y = int(centre_pixel[0]) # row
        img_height,img_width,_ = img_raw.shape
        _, pix_add_x, _ = pixels_for_ratio(img_height, img_width)
        width_calc = img_width + pix_add_x
        corner_pixels = getcontourcorners(shape_contour)
        x1 = int(corner_pixels[0][1]) # column
        y1 = int(corner_pixels[0][0]) # row
        x2 = int(corner_pixels[1][1]) # column
        y2 = int(corner_pixels[1][0]) # row
        r_v, g_v, b_v = list(shape_colour)
        colour_assign = (int(r_v),int(g_v),int(b_v))
        rectangles.append([(x1,y1),(x2,y2),colour_assign, (x2-x1)*(y2-y1)])
    max_rectangle = 0
    index_max = None
    for rectangle in rectangles:
        if rectangle[3] > max_rectangle:
            max_rectangle = rectangle[3]
            index_max = rectangle
    rectangles.remove(index_max)
    for rectangle in rectangles:
        cv2.rectangle(img_raw,rectangle[0],rectangle[1],rectangle[2],3)
    return img_raw

def mark_labels(img_raw,img_instances, img_labels):
    ins_colours = get_unique_colours_2(img_instances)
    rectangles = []
    for shape_colour in ins_colours:
        shape_pixels = getobject(img_instances, shape_colour)
        #print(shape_pixels[0])
        shape_contour = getcontour(shape_pixels)
        centre_pixel = getcontourcentre(shape_contour)
        # get the colour for centre pixel from labels
        x = int(shape_contour[0][1]) # column
        y = int(shape_contour[0][0]) # row
        colour_in_lbl = img_labels[y,x]
        img_height,img_width,_ = img_raw.shape
        _, pix_add_x, _ = pixels_for_ratio(img_height, img_width)
        width_calc = img_width + pix_add_x
        corner_pixels = getcontourcorners(shape_contour)
        x1 = int(corner_pixels[0][1]) # column
        y1 = int(corner_pixels[0][0]) # row
        x2 = int(corner_pixels[1][1]) # column
        y2 = int(corner_pixels[1][0]) # row
        if x2 >= img_width:
            x2 = img_width-1
        if y2 >= img_height:
            y2 = img_height-1
        r_v, g_v, b_v = list(colour_in_lbl)
        colour_assign = (int(r_v),int(g_v),int(b_v))
        
        #cv2.rectangle(img_raw,(x1,y1),(x2,y2),colour_assign,3)
        rectangles.append([(x1,y1),(x2,y2),colour_assign, (x2-x1)*(y2-y1)])
    max_rectangle = 0
    index_max = None
    for rectangle in rectangles:
        if rectangle[3] > max_rectangle:
            max_rectangle = rectangle[3]
            index_max = rectangle
    rectangles.remove(index_max)
    for rectangle in rectangles:
        cv2.rectangle(img_raw,rectangle[0],rectangle[1],rectangle[2],3)
    return img_raw

def mark_labels2(img_raw, img_labels):
    img_height,img_width,_ = img_raw.shape
    lbl_colours = get_unique_colours_2(img_labels)
    for colour in lbl_colours:
        if tuple(colour) != tuple([0,0,0]):
            #print(colour)
            shape_pixels = getobject(img_labels, colour)
            shape_contour = getcontour(shape_pixels)
            for indx in range(0, len(shape_contour)):
                x1 = int(shape_contour[indx][1]) # column
                y1 = int(shape_contour[indx][0]) # row
                img_raw[y1][x1] = colour
                neighbours = getadjacentpixels(shape_contour[indx], img_height, img_width)
                for pix in neighbours:
                    x1 = pix[1]
                    y1 = pix[0]
                    img_raw[y1][x1] = colour
    return img_raw
                   
def mark_images(image_file, instances_file, labels_file):
    img_raw = cv2.imread(image_file)
    img_labels = cv2.imread(labels_file)
    img_instances = cv2.imread(instances_file)
    img_marked = mark_instances(img_raw.copy(),img_instances)
    ins_marks = image_file[:-4] + "_instances.jpg"

    cv2.imwrite(ins_marks,img_marked)
    img_marked = mark_labels(img_raw.copy(),img_instances,img_labels)
    lbl_marks = image_file[:-4] + "_labels.jpg"
    cv2.imwrite(lbl_marks,img_marked)


# get the data from the csv_file, assuming first column is integer id
def get_csv_data(input_file):
    csv_data = {}
    fieldnames=[]
    int_indx = 1
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            csv_data[int_indx]=row
            int_indx +=1 
    return csv_data


def get_gbu(argv):
    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), 'Arguments:', argv)
    try:
        predictions_dir = argv[0]
        predictions_file = argv[1]
    except:
        print("provide two arguments:"+
              "\n -string predictions path\n -string predictions data file")
        return

    records = get_csv_data(predictions_dir+predictions_file)

    # calculate max, min, median and average for all even records
    max_diff = 0
    max_indx = 0
    min_diff = 0
    min_indx = 0
    mean_diff = 0
    mean_indx = 0
    for int_indx in records:
        current_val  = float(records[int_indx]['cls_diff_avg'])
        if int_indx %2 == 0: 
            if max_diff == min_diff == 0:
                max_diff = min_diff = current_val
            elif current_val > max_diff:
                max_diff = current_val
                max_indx = int_indx 
            elif current_val < min_diff:
                min_diff = current_val
                min_indx = int_indx
            mean_diff += current_val

    mean_diff = mean_diff/(len(records)/2)

    close_match = 0 
    for int_indx in records:
        current_val  = float(records[int_indx]['cls_diff_avg'])
        if int_indx %2 == 0:
            if mean_indx == 0:
                close_match = current_val
                mean_indx = int_indx
            elif abs(mean_diff-close_match) > abs(mean_diff-current_val):
                mean_indx = int_indx
                close_match = current_val
        
    print(len(records), max_diff,max_indx,min_diff, min_indx, mean_diff, mean_indx)

    # mark images for max
    print("worst prediction:", records[max_indx]['image'])
    im_file = predictions_dir + records[max_indx]['image']
    ins_file = im_file[:-4] + "_instances.png"
    lbl_file = im_file[:-4] + "_labels.png"


    mark_images(im_file, ins_file, lbl_file)

    # mark images for min
    print("best prediction:", records[min_indx]['image'])
    im_file = predictions_dir + records[min_indx]['image']
    ins_file = im_file[:-4] + "_instances.png"
    lbl_file = im_file[:-4] + "_labels.png"


    mark_images(im_file, ins_file, lbl_file)
    print("average prediction:", records[mean_indx]['image'])
    im_file = predictions_dir + records[mean_indx]['image']
    ins_file = im_file[:-4] + "_instances.png"
    lbl_file = im_file[:-4] + "_labels.png"

    mark_images(im_file, ins_file, lbl_file)

if __name__ == "__main__":
    get_gbu(sys.argv[1:])
    
predictions_dir = '/home/abraham/semseghs/predictions/model_nhm_data_nhm/'
file_name = '010668463_816414_1428267.JPG' # worst
file_name = '010646759_816445_1431072.JPG' # best
#file_name = '010653012_816393_1428658.JPG' # average
im_file = predictions_dir + file_name
ins_file = im_file[:-4] + "_instances.png"
lbl_file = im_file[:-4] + "_labels.png"
img_instances = cv2.imread(ins_file)
img_labels = cv2.imread(lbl_file)
img_labels = cv2.imread(lbl_file)
img_raw = cv2.imread(im_file)
marked_img = mark_labels2(img_raw.copy(), img_labels)

cv2.imshow('image', marked_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
