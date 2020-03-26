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


# image file to process
print("Start",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
img = io.imread('test/predictions/010653012_816393_1428658_labels.png')

# get image size and number of pixel elements
rows, cols, bands = img.shape
print("Image dimensions (rows, cols, bands):",rows, cols, bands)
# discard alpha channel
if bands > 3:
    img = img[:,:,:3]
    bands = 3

# get a list of colour with pixel count
colours_list = get_colours_list(img)
# get number of unique colours
num_clusters = len(colours_list)

for this_colour in colours_list:
    print(this_colour)
    if this_colour not in [(0, 0, 0), (0, 0, 0, 255)]:
        object_pixels = getobject(img, this_colour)
        contour_pixels = getcontour(object_pixels)
        all_paths  = get_all_paths(contour_pixels)
        print('Colour: {}  >>  Objects: {}'.format(this_colour, len(all_paths)))
    

print("MID",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
X = img.reshape(rows*cols, bands)

x_rows, x_bands = X.shape
print (x_rows, x_bands)

kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(X)
labels = kmeans.labels_.reshape(rows, cols)

for i in np.unique(labels):
    blobs = np.int_(morphology.binary_opening(labels == i))
    print(len(blobs))
    color = np.around(kmeans.cluster_centers_[i])
    count = len(np.unique(measure.label(blobs))) - 1
    print('Color: {}  >>  Objects: {}'.format(color, count))
print("END",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
