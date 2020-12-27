import numpy as np
from datetime import datetime
from pathlib import Path
import sys
import cv2

# add results to a DB
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    # create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn
        else:
            conn.close()
            
def create_table(conn, create_table_sql):
    # create a table from the create_table_sql statement
    # :param conn: Connection object
    # :param create_table_sql: a CREATE TABLE statement
    # :return:
    
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_obj(conn, table, obj):
    obj_keys = ""
    obj_values = ""
    for key in obj:
        if obj_keys =="":
            obj_keys = key
            obj_values = "'" + str(obj[key]) + "'"
        else:
            obj_keys += ", " + key
            obj_values += ", '" + str(obj[key]) + "'"
    insert_stmt = "INSERT INTO {} ({}) VALUES ({})".format(table, obj_keys, obj_values)
    
    cur = conn.cursor()
    cur.execute(insert_stmt)
    conn.commit()
    return cur.lastrowid

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
            contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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

# ground truth dataset
def get_gt_values(argv):
    print("Start",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    print('Arguments:', argv)
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
    conn = create_connection(r"gtprv_ms.sqlite")
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

    print("Files: ", file_list)

    for filename in file_list:
        
        # GT labels file
        gt_lbl = Path(labels_dir, filename+'_labels.png')
        # GT instances file
        gt_ins = Path(instances_dir, filename+'_instances.png')
        # predictions labels file
        pr_lbl = Path(pr_dir, filename+'_labels.png')
        # predictions instances file
        pr_ins = Path(pr_dir, filename+'_instances.png')
        #print(gt_lbl,"\n",gt_ins,"\n",pr_lbl, "\n",pr_ins)
        pr_lbl_img = cv2.imread(str(pr_lbl))
        rows, cols, bands = pr_lbl_img.shape
        #show_image(pr_lbl_img, "PR labels")
        gt_lbl_img = cv2.imread(str(gt_lbl))
        #show_image(gt_lbl_img, "GT labels")
        #***************************************************
        # Calculate TP, TN, FP, and FN for earch prediction
        #***************************************************
        # a) open the GT instance file
        # b) for each colour in the instance, get borders
        gt_ins_img = cv2.imread(str(gt_ins))
        gt_objects = get_img_contours(gt_ins_img)
        # c) get the types assigned to each object fragment in predictions and GT
        # d) compare to GT labels  to get TP and FP
        for an_object in gt_objects:
            for fragment in gt_objects[an_object]:
                f_centre = get_cnt_centre(fragment)
                if f_centre[0] >= rows:
                    f_centre = (-1, f_centre[1])
                if f_centre[1] >= cols:
                    f_centre = (f_centre[0], cols -1)    
                gt_class = tuple(gt_lbl_img[f_centre])
                pr_class = tuple(pr_lbl_img[f_centre])
                ob_values = {"file":filename, "source":"GT", "obj_colour":an_object, "ground_truth":gt_class, "predicted":pr_class}
                new_id = insert_obj(conn, table_name, ob_values)
                print("inserted object:", ob_values, "with id:", new_id)  

        # f) open the predictions instance file
        # g) for each colour in the instance, get borders.
        pr_ins_img = cv2.imread(str(pr_ins))
        pr_objects = get_img_contours(pr_ins_img)
        # h) get the types assigned to each object fragment in predictions and GT
        # i) compare to GT labels  to get TP and FP
        for an_object in pr_objects:
            for fragment in pr_objects[an_object]:
                f_centre = get_cnt_centre(fragment)
                if f_centre[0] >= rows:
                    f_centre = (-1, f_centre[1])
                if f_centre[1] >= cols:
                    f_centre = (f_centre[0], cols -1)    
                gt_class = tuple(gt_lbl_img[f_centre])
                pr_class = tuple(pr_lbl_img[f_centre])
                ob_values = {"file":filename, "source":"PR", "obj_colour":an_object, "ground_truth":gt_class, "predicted":pr_class}
                new_id = insert_obj(conn, table_name, ob_values)
                print("inserted object:", ob_values, "with id:", new_id)
                
    print("Finish: ",datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    # i) categorise results to obtain TP, TN, FP and FN for each file
    # Add to DB, use queries to summarise
    conn.close()
	
if __name__ == "__main__":
   get_gt_values(sys.argv[1:])
