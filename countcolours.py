import numpy as np
from skimage import io, morphology, measure
from sklearn.cluster import KMeans
from datetime import datetime

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


print("Start",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

filename = "010668463_816414_1428267"
filename = "010653012_816393_1428658"
filename = "010646759_816445_1431072"

# GT labels file
gt_lbl = 'test/data/raw/labels/{}_labels.png'.format(filename) # labels_path / gt_data[indx]['labels']
# GT instances file
gt_ins = 'test/data/raw/instances/{}_instances.png'.format(filename) # instances_path / gt_data[indx]['instances']
#print(predictions_path)
# predictions labels file
pr_lbl = 'test/predictions/{}_labels.png'.format(filename) # predictions_path / gt_data[indx]['labels']
# predictions instances file
pr_ins = 'test/predictions/{}_instances.png'.format(filename) # predictions_path / gt_data[indx]['instances']

#***************************************************
# Calculate TP, TN, FP, and FN for earch prediction
# a) open the predictions instance file
# b) for each colour in the instance, get borders.
pr_objects = get_shapes_per_colour(pr_ins)

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


pr_values = {}
indx = 1
for an_object in pr_objects:
    print('Colour: {}  >>  Fragments: {}'.format(an_object, len(pr_objects[an_object])))
    # c) get the types assigned to each object fragment in predictions and GT
    # d) compare to GT labels  to get TP and FP
    for fragment in pr_objects[an_object]:
        f_centre = getcontourcentre(fragment)
        assign_pr_class = assignclass(fragment, pr_lbl_img)
        gt_class = tuple(gt_lbl_img[f_centre])
        print(an_object, "ground truth:",gt_class, "predicted:", assign_pr_class)
        pr_values[indx] = {"obj_colour":an_object, "ground truth":gt_class, "predicted":assign_pr_class}
        indx +=1

print("PR Done ",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))        
#***************************************************
# e) open the GT instance file
# f) for each colour in the instance, get borders

gt_objects = get_shapes_per_colour(gt_ins)

gt_values = {}
indx = 1
for an_object in gt_objects:
    print('Colour: {}  >>  Fragments: {}'.format(an_object, len(gt_objects[an_object])))
    # g) get the types assigned to each object in GT
    # h) comparte to  PR labels to get FN
    for fragment in gt_objects[an_object]:
        f_centre = getcontourcentre(fragment)
        pr_class = tuple(pr_lbl_img[f_centre])
        gt_class = tuple(gt_lbl_img[f_centre])
        print(an_object, "ground truth:",gt_class, "predicted:", pr_class)
        gt_values[indx] = {"obj_colour":an_object, "ground truth":gt_class, "predicted":pr_class}
        indx +=1
    
print("GT Done",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
