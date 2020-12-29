import numpy as np
from datetime import datetime
from pathlib import Path
import csv
import sys
import cv2

# get list of unique colour, with a count of the pixels
def get_colours_list(img):
    aimg= np.asarray(img)
    return set( tuple(v) for m2d in aimg for v in m2d )

# retrieve test files using tr/ts proportions
def test_files_list(source_dir,tr=8,ts=2):
    i_counter = 0
    files_list = []
    for filepath in sorted(source_dir.glob('*.JPG')):
        i_counter += 1
        if i_counter > tr:
            files_list.append(Path(filepath).name[:-4])
            if i_counter == tr+ts:
                i_counter = 0
    return files_list

def show_image(img_arr, title = "test"):
    cv2.imshow(title, img_arr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_img_contours(im):
    #show_image(im, "gt instances")
    colours_list = get_colours_list(im)
    backgrounds_skip = [(0, 0, 0)]
    background_clr = tuple(im[0,0])
    if not background_clr in backgrounds_skip:
      backgrounds_skip.append(background_clr)

    img_contours = {}
    for this_colour in colours_list:
        if not this_colour in backgrounds_skip:
            test = im.copy()
            for mk_black in colours_list:
                if mk_black != this_colour:
                    test[np.all(test == mk_black, axis=-1)] = (0,0,0)
            test[np.all(test == this_colour, axis=-1)] = (255,255,255)
            #show_image(test, "img copy blob")
            imgray = cv2.cvtColor(test,cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)
            _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            # the raven version needs the line below instead of the line above
            #an_img, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            img_contours[this_colour]=contours
    return img_contours

def get_cnt_centre(cnt):
    M = cv2.moments(cnt)
    c_ctr = None
    if M['m00']!=0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        c_ctr = (cy,cx)
    else:
        c_ctr = get_cnt_centre2(cnt)
    return c_ctr

# get the corners of the circunscribed rectangle
def get_cnt_corners(shape_contour):
    min_x = min_y = max_x = max_y = 0
    for pair in shape_contour:
        if min_x==min_y==max_y==max_x==0:
            min_y, min_x = pair[0]
            max_y, max_x = pair[0]
        else:
            if pair[0][0] < min_y:
                min_y = pair[0][0]
            if pair[0][1] < min_x:
                min_x = pair[0][1]
            if pair[0][0] > max_y:
                max_y = pair[0][0]
            if pair[0][1] > max_x:
                max_x = pair[0][1]
    return ((min_y, min_x), (max_y, max_x))

# get the centre pixel for the circunscribed object
def get_cnt_centre2(shape_contour):
    min_x = min_y = max_x = max_y = 0
    ((min_y, min_x), (max_y, max_x)) = get_cnt_corners(shape_contour)
    mid_y = int(round(min_y + (max_y-min_y)/2))
    mid_x = int(round(min_x + (max_x-min_x)/2))
    return (mid_y, mid_x)

def get_files_list(str_path, partial_limit = 0):
    i_counter = 0
    files_list = []
    for filepath in sorted(Path(str_path).glob('*.JPG')):
        i_counter += 1
        files_list.append(Path(filepath).name[:-4])
        print(i_counter, filepath)
        if partial_limit != 0 and i_counter == partial_limit:
            break    
    return files_list

def get_label(color_val, label_colors):
    label_str = ""
    for val in label_colors:
        if label_colors[val][0] == color_val:
            label_str = label_colors[val][1]
    return label_str

# writes data to the given file name
def write_csv_data(values, filename):
    fieldnames = []
    for item in values.keys():
        for key in values[item].keys():
            if not key in fieldnames:
                fieldnames.append(key)
    #write back to a new csv file
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in values.keys():
            writer.writerow(values[key])

def build_yolo_gt(argv, label_colors = None):
    print("Start: ",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    print('Arguments:', argv)
    try:
        gt_path = argv[0]
        out_file = argv[1]
    except:
        print("missing arguments:"+
              "\n -ground truths path"+
              "\n -output filename (csv)")
        return
    files_list = get_files_list(gt_path, 10)
    print(len(files_list), files_list)
    indx = 0
    ob_values = {}
    for filename in files_list:    
        # GT labels file
        gt_lbl = Path(gt_path, filename+'_labels.png')
        print(gt_lbl)
        # GT instances file
        gt_ins = Path(gt_path, filename+'_instances.png')
        print(gt_ins)
        gt_lbl_img = cv2.imread(str(gt_lbl))
        #show_image(gt_lbl_img, "GT labels")
        # a) open the GT instance file
        # b) for each colour in the instance, get borders
        gt_ins_img = cv2.imread(str(gt_ins))
        #show_image(gt_ins_img, "GT instances")
        gt_objects = get_img_contours(gt_ins_img)
        #print(gt_objects)
        # c) get the types assigned to each object fragment in predictions and GT
        # d) compare to GT labels  to get TP and FP
        for an_object in gt_objects:
            for fragment in gt_objects[an_object]:
                f_centre = get_cnt_centre(fragment)
                if f_centre[0] >= 300:
                    f_centre = (-1, f_centre[1])
                if f_centre[1] >= 800:
                    f_centre = (f_centre[0], cols -1)    
                gt_class = tuple(gt_lbl_img[f_centre]/255)
                class_lbl = get_label(gt_class, label_colors)
                gt_corners = get_cnt_corners(fragment)
                ob_values[indx] = {"file":filename, "gt_class":gt_class,
                             "class_lbl":class_lbl,"centre_x":f_centre[1],
                             "centre_y":f_centre[0], "tr_x":gt_corners[0][0],
                             "tr_y":gt_corners[0][1], "ll_x":gt_corners[1][0],
                             "ll_y":gt_corners[1][1]}
                indx +=1
        print("objects:", len(ob_values))  

    write_csv_data(ob_values,out_file)

    print("End:   ",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

if __name__ == "__main__":
    label_colors = {1:[(0.0,0.0,0.0),'background'],2:[(1.0,1.0,1.0),'barcode'],
                3:[(1.0,0.0,0.0),'typelabel'],4:[(0.0,1.0,1.0),'specimen'],
                5:[(0.0,0.0,1.0),'label']}
    build_yolo_gt(sys.argv[1:], label_colors)
