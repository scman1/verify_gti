import numpy as np
from skimage import io#, morphology, measure
#from sklearn.cluster import KMeans
from datetime import datetime
import csv
from pathlib import Path
import sys

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

# get list of unique colour, with a count of the pixels
def get_colours_list(img):
    aimg= np.asarray(img)
    return set( tuple(v) for m2d in aimg for v in m2d )

#get contour pixels from an object
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

# get all pixel coordinates for a given colour
def getobject(img, colour):
    indices = np.where(np.all(np.array(img) == colour, axis=-1))
    pixels = list(zip(indices[0], indices[1]))
    return pixels

# split the indeppedent paths in a large set of nodes
def get_neighbours(point, all_points):
    x = point[0]
    y = point[1]

    other_points = set(all_points)
    
    adjacent_points  = [(x-1,y),(x-1,y-1),(x-1,y+1),(x,y+1),(x,y-1),(x+1,y-1),(x+1,y),(x+1,y+1)]
    neighbours = []
    for pt in adjacent_points:
        if pt in other_points:
            neighbours.append(pt)
    return neighbours

# get the points which are 
def get_extremes(path_set, all_points):
    extremes = []
    path_set = set(path_set)
    for point in path_set:
        point_neighbours = set(get_neighbours(point, all_points))
        diff_set = list(point_neighbours.difference(path_set))
        if len(diff_set) != 0:
            extremes.append(point)
    return extremes

# starting from a point in the borders get all which are together
def get_path(start, big_set):
    path_set = []
    neighbours = get_neighbours(start, big_set)
    #print("point:",start,"neighbours:",neighbours)
    path_set = [*neighbours]
    path_set.append(start)

    while True:
        extremes  = get_extremes(path_set, big_set)
        if extremes == []:
            break
        for extreme in extremes:
            #print ("extremes", extreme)
            start = extreme
            neighbours = get_neighbours(start, big_set)
            path_set = [*path_set, *list(set(neighbours).difference(set(path_set)))]
    return path_set

# get the corners of the circunscribed rectangle
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

# get the centre pixel for the circunscribed object
def getcontourcentre(shape_contour):
    min_x = min_y = max_x = max_y = 0
    ((min_y, min_x), (max_y, max_x)) = getcontourcorners(shape_contour)
    mid_y = int(round(min_y + (max_y-min_y)/2))
    mid_x = int(round(min_x + (max_x-min_x)/2))
    return (mid_y, mid_x)

# verify if the path is a hole,
# i.e. contained inside another path
def is_hole(single_path, all_paths):
    for one_path in all_paths:
        if set(single_path) != set(one_path ):
            if len(single_path) < len(one_path):
                ((e,f),(g,h)) = getcontourcorners(single_path)
                ((a,b),(c,d)) = getcontourcorners(one_path)
                if e >= a and e <= c and \
                   f >= b and f <= d and \
                   g >= a and g <= c and \
                   h >= b and h <= d:
                    return True
    return False

def contourcolours(shape_contour, lbl_img):
    contour_colours = {}
    for point in shape_contour:
        point_colour = tuple(lbl_img[point])
        if point_colour in contour_colours.keys():
            contour_colours[point_colour] += 1
        else:
            contour_colours[point_colour] = 1
    return contour_colours

# use the colours on the borders to determine
# an objects class, the proportion
def assignclass(shape_contour, lbl_img):
    contour_colours = contourcolours(shape_contour, lbl_img)
    class_colour = tuple()
    max = 0
    for contour_colour in contour_colours:
        if max == 0:
            max = contour_colours[contour_colour]
            class_colour = contour_colour
        elif max < contour_colours[contour_colour]:
            max = contour_colours[contour_colour]
            class_colour = contour_colour
            
    return class_colour
        

# get all closed independent paths in a set of points
def get_all_paths(big_set):
    not_inspected = big_set
    all_paths = []
    while not_inspected  != []:
        path_set = get_path(not_inspected[0], not_inspected)
        not_inspected = [*list(set(not_inspected).difference(set(path_set)))]
        all_paths.append(path_set)
    # need to remove wholes which are also detected as paths            
    holes=[]
    for single_path in all_paths:
        if is_hole(single_path, all_paths):
            holes.append(single_path)
    if len(holes) != 0:
        for a_hole in holes:
            all_paths.remove(a_hole)
    return all_paths


#***************************************
# A-B) open predictions file and
#      object get borders
# Returns:
#      Dictionary with colours as keys
#      and shape borders lists as
#      elements
#        {(colour): [(paths),...]}
#***************************************
def get_shapes_per_colour(filename):
    img = io.imread(filename)

    # get image size and number of pixel elements
    rows, cols, bands = img.shape
    # discard alpha channel
    if bands > 3:
        img = img[:,:,:3]
        bands = 3
    # get a list of colour with pixel count
    colours_list = get_colours_list(img)
    # get number of unique colours
    num_clusters = len(colours_list)
    # identify background colour
    backgrounds_skip = [(0, 0, 0)]
    background_clr = tuple(img[0,0])
    if not background_clr in backgrounds_skip:
        backgrounds_skip.append(background_clr)
    #get all shapes for each colour
    objects = {}
    for this_colour in colours_list:
        #print(this_colour)
        if not this_colour in backgrounds_skip:
            object_pixels = getobject(img, this_colour)
            contour_pixels = getcontour(object_pixels)
            all_paths  = get_all_paths(contour_pixels)
            objects[this_colour] = all_paths
    return objects

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

# ground truth dataset
def get_gt_values(argv,label_colors=None):
    print("Start",datetime.now().strftime("%Y/%m/%d %H:%M:%S"), 'Arguments:', argv)
    try:
        gt_path = argv[0]
        pr_path = argv[1]
        out_file = argv[2]
        train_prop = int(argv[3])
        test_prop = int(argv[4])
    except:
        print("provide five arguments:"+
              "\n -string ground truths path\n -string predictions path"+
              "\n -string output filename (csv)\n -integer proportion train set"+
              "\n -integer proportion test/eval set")
        return
    # insert objects directly into SQLite DB
    # set table name
    table_name = out_file[:-4]
    # create DB
    conn = create_connection(r"hs_gtprverify.sqlite")
    # create table
    create_stmt = " CREATE TABLE IF NOT EXISTS "+ table_name + \
                  "(id integer PRIMARY KEY, file text, " + \
                  "source text, obj_colour text, ground_truth text, "+ \
                  "predicted text); "
    create_table(conn, create_stmt)

    
    gt_dir= Path(gt_path)
    # predictions dataset
    pr_dir = Path(pr_path)
    # paths for ground truth set on semseg directory
    images_dir = gt_dir / 'images'
    labels_dir = gt_dir / 'labels'
    instances_dir = gt_dir / 'instances'

    
    # get a list of the files to compare
    file_list = test_files_list(images_dir,train_prop,test_prop)

    print("Start",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    print(file_list)

    ob_values = {}
    indx = 1

    for filename in file_list:
        # GT labels file
        gt_lbl = Path(labels_dir, filename+'_labels.png')
        # GT instances file
        gt_ins = Path(instances_dir, filename+'_instances.png')
        # predictions labels file
        pr_lbl = Path(pr_dir, filename+'_labels.png')
        # predictions instances file
        pr_ins = Path(pr_dir, filename+'_instances.png')

        pr_lbl_img = io.imread(pr_lbl)
        # get image size and number of pixel elements
        rows, cols, bands = pr_lbl_img.shape
        # discard alpha channel
        if bands > 3:
            pr_lbl_img = pr_lbl_img[:,:,:3]
            bands = 3
        gt_lbl_img = io.imread(gt_lbl)
        # get image size and number of pixel elements
        rows, cols, bands = gt_lbl_img.shape
        # discard alpha channel
        if bands > 3:
            gt_lbl_img = gt_lbl_img[:,:,:3]
            bands = 3

        #print(gt_ins, gt_lbl, pr_ins, pr_lbl)
        #***************************************************
        # Calculate TP, TN, FP, and FN for earch prediction
        #***************************************************
        # e) open the GT instance file
        # f) for each colour in the instance, get borders
        gt_objects = get_shapes_per_colour(gt_ins)

        for an_object in gt_objects:
            print('Colour: {}  >>  Fragments: {}'.format(an_object, len(gt_objects[an_object])))
            # g) get the types assigned to each object in GT
            # h) comparte to  PR labels to get FN
            for fragment in gt_objects[an_object]:
                f_centre = getcontourcentre(fragment)
                pr_class = tuple(pr_lbl_img[f_centre])
                gt_class = tuple(gt_lbl_img[f_centre])
                print(an_object, "ground_truth:",gt_class, "predicted:", pr_class)
                ob_values[indx] = {"file":filename, "source":"GT","obj_colour":an_object, "ground_truth":gt_class, "predicted":pr_class}
                new_id = insert_obj(conn, table_name, ob_values[indx])
                print("inserted object with id:", new_id)
                indx +=1
            
        print("file:",filename, "GT Done",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        #print(ob_values)
        # a) open the predictions instance file
        # b) for each colour in the instance, get borders.
        pr_objects = get_shapes_per_colour(pr_ins)

        for an_object in pr_objects:
            print('Colour: {}  >>  Fragments: {}'.format(an_object, len(pr_objects[an_object])))
            # c) get the types assigned to each object fragment in predictions and GT
            # d) compare to GT labels  to get TP and FP
            for fragment in pr_objects[an_object]:
                f_centre = getcontourcentre(fragment)
                # correct for difference in size of images
                if f_centre[0] >= rows:
                    f_centre = (-1, f_centre[1])
                if f_centre[1] >= cols:
                    f_centre = (f_centre[0], cols -1)    
                assign_pr_class = assignclass(fragment, pr_lbl_img)
                gt_class = tuple(gt_lbl_img[f_centre])
                print(an_object, "ground_truth:",gt_class, "predicted:", assign_pr_class)
                ob_values[indx] = {"file":filename, "source":"PR", "obj_colour":an_object, "ground_truth":gt_class, "predicted":assign_pr_class}
                new_id = insert_obj(conn, table_name, ob_values[indx])
                print("inserted object with id:", new_id)
                indx +=1
        #print(ob_values)
        print("file:",filename, "PR Done ",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))        
        
    print("fragments detected:", indx)

    write_csv_data(ob_values,out_file)

    # i) categorise results to obtain TP, TN, FP and FN for each file
    # Add to DB, use queries to summarise

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


def build_yolo_gt(argv, label_colors=None):
    print("Start: ",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    print('Arguments:', argv)
    try:
        gt_path = argv[0]
        out_file = argv[1]
    except:
        print("provide five arguments:"+
              "\n -string  ground truths path")
        return
    files_list = get_files_list(gt_path,0)    
    #print(len(files_list), files_list)

    indx = 0
    ob_values = {}
    for filename in files_list:    
        # GT labels file
        gt_lbl = Path(gt_path, filename+'_labels.png')
        #print(gt_lbl)
        # GT instances file
        gt_ins = Path(gt_path, filename+'_instances.png')
        #print(gt_ins)
        gt_lbl_img = io.imread(str(gt_lbl))
        # get image size and number of pixel elements
        rows, cols, bands = gt_lbl_img.shape
        # discard alpha channel
        if bands > 3:
            gt_lbl_img = gt_lbl_img[:,:,:3]
            bands = 3
        # a) open GT instance file and get the objects
        # for each colour in the instance
        gt_objects = get_shapes_per_colour(gt_ins)

        
        #print(gt_objects)
        # c) get the types assigned to each object fragment in predictions and GT
        # d) compare to GT labels  to get TP and FP
        for an_object in gt_objects:
            for fragment in gt_objects[an_object]:
                f_centre = getcontourcentre(fragment)
                gt_class = assignclass(fragment, gt_lbl_img)
                class_lbl = get_label(gt_class, label_colors)
                gt_corners = getcontourcorners(fragment)
                ob_values[indx] = {"file" : filename, "gt_class" : gt_class,
                             "class_lbl" : class_lbl,"centre_x" : f_centre[1],
                             "centre_y" : f_centre[0], "tr_x": gt_corners[0][0],
                             "tr_y": gt_corners[0][1], "ll_x": gt_corners[1][0],
                             "ll_y": gt_corners[1][1],
                             "height": gt_corners[1][0]-gt_corners[0][0],
                             "width": gt_corners[1][1] -gt_corners[0][1],
                             "yolo_cx":f_centre[1]/cols, "yolo_cy": f_centre[0]/rows,
                             "yolo_height": (gt_corners[1][0]-gt_corners[0][0])/rows,
                             "yolo_width": (gt_corners[1][1] -gt_corners[0][1])/cols}
                #new_id = insert_obj(conn, table_name, ob_values)
                #print("object:", ob_values)#, "with id:", new_id)  
    write_csv_data(ob_values,out_file)
    print("End:   ",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))


if __name__ == "__main__":
  label_colors = {1:[(0.0,0.0,0.0),'background'],2:[(1.0,1.0,1.0),'barcode'],
                3:[(1.0,0.0,0.0),'label'],4:[(1.0,1.0,0.0),'specimen'],
                5:[(0.0,0.0,1.0),'typelabel']}
  # get_gt_values(sys.argv[1:], label_colors)
  build_yolo_gt(sys.argv[1:], label_colors)
