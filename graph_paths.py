

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
        #print(point)
        point_neighbours = set(get_neighbours(point, all_points))
        #print(point_neighbours)
        diff_set = list(point_neighbours.difference(path_set))
        #print("diff:",diff_set)
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

big_set = [(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(3,2),(3,8),(4,2),(4,8),(5,2),(5,8),(5,9),(5,12),(5,13),(5,14),(6,2),(6,9),(6,12),(6,14),(7,2),(7,8),(7,9),(7,12),(7,13),(7,14),(8,2),(8,8),(9,2),(9,3),(9,4),(9,5),(9,6),(9,7),(9,8)]
start = (5,12)
start = (2,2)



##path_set = get_path((5,8), not_inspected)
##print (len(path_set), path_set)
##
##not_inspected = [*list(set(not_inspected).difference(set(path_set)))]
##print (not_inspected)

all_paths  = get_all_paths(big_set)
print(len(all_paths))
for single_path in all_paths:
    print(len( single_path), single_path)
