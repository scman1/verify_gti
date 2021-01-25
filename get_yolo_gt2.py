import numpy as np
from skimage import io#, morphology, measure
from datetime import datetime
from pathlib import Path
import csv
import sys
from tqdm import tqdm

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

#****************************************
# open gt file and get objects per colour
#
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

def get_files_list(str_path, partial_limit = 0):
    i_counter = 0
    files_list = []
    for filepath in sorted(Path(str_path).glob('*.JPG')):
        i_counter += 1
        files_list.append(Path(filepath).name[:-4])
        #print(i_counter, filepath)
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
        print("provide arguments:"+
              "\n -string  ground truths path"+
              "\n -string output filename")
        return
    # get the list of image files
    files_list = get_files_list(gt_path,0)    
    
    indx = 0
    ob_values = {}
    # for each file get gt instances and
    # assing class to each instance
    for filename in tqdm(files_list):    
        # set GT labels[class] file name
        gt_lbl = Path(gt_path, filename+'_labels.png')
        # set GT instances file
        gt_ins = Path(gt_path, filename+'_instances.png')
        # read class file
        gt_lbl_img = io.imread(str(gt_lbl))
        # get image size and number of pixel elements
        rows, cols, bands = gt_lbl_img.shape
        # discard alpha channel
        if bands > 3:
            gt_lbl_img = gt_lbl_img[:,:,:3]
            bands = 3
        # open GT instance file and get individual
        # objects per colour
        gt_objects = get_shapes_per_colour(gt_ins)

        # assing class to each object
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
                indx += 1
    # save results in ouptut file
    write_csv_data(ob_values,out_file)
    print("End:   ",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))


if __name__ == "__main__":
  label_colors = {1:[(0.0,0.0,0.0),'background'],2:[(1.0,1.0,1.0),'barcode'],
                3:[(1.0,0.0,0.0),'label'],4:[(1.0,1.0,0.0),'specimen'],
                5:[(0.0,0.0,1.0),'typelabel']}
  # get_gt_values(sys.argv[1:], label_colors)
  build_yolo_gt(sys.argv[1:], label_colors)
