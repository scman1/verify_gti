

# split the indeppedent paths in a large set of nodes
def get_neighbours(point, all_points):
    x = point[0]
    y = point[1]

    other_points = set(all_points)
    
    adjacent_points  = [(x-1,y),(x-1,y-1),(x-1,y+1),(x,y+1),(x,y-1),(x+1,y-1),(x+1,y),(x+1,y+1)]
    neighbours = set()
    for pt in adjacent_points:
        if pt in other_points:
            neighbours = neighbours.union({pt})
    return neighbours

# get the points which are 
def get_extremes(path_set, all_points):
    extremes = []
    #extremes = set()
    path_set = set(path_set)
    for point in path_set:
        #print(point)
        point_neighbours = get_neighbours(point, all_points)
        print(point_neighbours)
        diff_set = point_neighbours.difference(path_set)
        
        if len(diff_set) != 0:
            extremes.append(point)
            #extremes = extremes.union({point})
    print (extremes)
    return extremes

# starting from a point in the borders get all which are together
def get_path(start, big_set):
    path_set = []
    neighbours = get_neighbours(start, big_set)
    #print("point:",start,"neighbours:",neighbours)
    path_set = [*neighbours]
    path_set.append(start)
    #print("path_set", path_set)
    while True:
        extremes  = get_extremes(path_set, big_set)
        if extremes == []:
            break
        for extreme in extremes:
            #print ("extremes", extreme)
            start = extreme
            neighbours = get_neighbours(start, big_set)
            #print("point:",start,"neighbours:",neighbours)
            path_set = [*path_set, *list(set(neighbours).difference(set(path_set)))]
            #print("path_set", path_set)
    return path_set

# get all closed independent paths in a set of points
def get_all_paths(big_set):
    not_inspected = big_set
    all_paths = []
    while not_inspected  != []:
        path_set = get_path(not_inspected[0], not_inspected)
        not_inspected = [*list(set(not_inspected).difference(set(path_set)))]
        #print (not_inspected)
        #print (len(path_set), path_set)
        all_paths.append(path_set)
    return all_paths

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
def is_hole(sigle_path, all_paths):
    for one_path in all_paths:
        if set(single_path) != set(one_path ):
            if len(single_path) < len(one_path):
                ((e,f),(g,h)) = getcontourcorners(single_path)
                ((a,b),(c,d)) = getcontourcorners(one_path)
                print(a,b,c,d)
                print(e,f,g,h)
                if e >= a and e <= c and \
                   f >= b and f <= d and \
                   g >= a and g <= c and \
                   h >= b and h <= d:
                    #print("**************************\n",single_path, "is really a hole of\n**************************\n", one_path)
                    #print (a,b,c,d)
                    return True
    return False
                

# two shapes
big_set = [(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(3,2),(3,8),(4,2),(4,8),(5,2),(5,8),(5,9),(5,12),(5,13),(5,14),(6,2),(6,9),(6,12),(6,14),(7,2),(7,8),(7,9),(7,12),(7,13),(7,14),(8,2),(8,8),(9,2),(9,3),(9,4),(9,5),(9,6),(9,7),(9,8)]
# with a hole in the largest shape
big_set = [(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(3,2),(3,8),(4,2),(4,8),(5,2),(5,8),(5,9),(5,12),(5,13),(5,14),(6,2),(6,9),(6,12),(6,14),(7,2),(7,8),(7,9),(7,12),(7,13),(7,14),(8,2),(8,8),(9,2),(9,3),(9,4),(9,5),(9,6),(9,7),(9,8),(4,4),(4,5),(4,6),(5,4),(5,6),(6,4),(6,5),(6,6)]
start = (5,12)
start = (2,2)



##path_set = get_path((5,8), not_inspected)
##print (len(path_set), path_set)
##
##not_inspected = [*list(set(not_inspected).difference(set(path_set)))]
##print (not_inspected)

all_paths  = get_all_paths(big_set)
print(len(all_paths))
holes=[]
for single_path in all_paths:
    print(len(single_path), single_path)
    if is_hole(single_path, all_paths):
        holes.append(single_path)
print (holes)
if len(holes) != 0:
    for a_hole in holes:
        all_paths.remove(a_hole)

