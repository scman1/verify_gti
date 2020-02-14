import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import csv

def test_files_list(source_dir,tr=8,ts=2):
    i_counter = 0
    files_list = []
    for filepath in sorted(source_dir.glob('*.JPG')):
        i_counter += 1
        if i_counter > tr:
            files_list.append(Path(filepath))
            if i_counter == tr+ts:
                i_counter = 0
    return files_list

def get_colours_list(img):
    aimg= np.asarray(img)
    return set( tuple(v) for m2d in aimg for v in m2d )

def get_colour_count(img):
    aimg= np.asarray(img)
    return Counter([tuple(colours) for i in aimg for colours in i])

def get_mean_area_diff(area1, area2):
    abs_diff = abs(area1-area2)
    diff1 = diff2 = 0
    if area1 != 0:
        diff1 = abs_diff/area1
    if area2 != 0:
        diff2 = abs_diff/area2
    return (diff1+diff2)/2

def read_gt_data(labels_path, instances_path, predictions_path, gt_data, label_colors):
    for indx in gt_data.keys():
        gt_lbl = labels_path / gt_data[indx]['labels']
        gt_ins = instances_path / gt_data[indx]['instances']
        #print(predictions_path)
        pr_lbl = predictions_path / gt_data[indx]['labels']
        pr_ins = predictions_path / gt_data[indx]['instances']        
        if gt_lbl.exists() and gt_lbl.is_file():
            gt_lbl_img = plt.imread(str(gt_lbl))
            # for labels the number of colours is the number of classes in the image
            gt_lbl_clrs = get_colour_count(gt_lbl_img)
            gt_data[indx]['gt_classes'] = len(gt_lbl_clrs)
            for color in label_colors:
                tag = "gt_"+label_colors[color][1]
                gt_data[indx][tag] = 0
                if(label_colors[color][0] in gt_lbl_clrs):
                    gt_data[indx][tag] = gt_lbl_clrs[label_colors[color][0]]
        if gt_ins.exists() and gt_ins.is_file():
            gt_ins_img = plt.imread(str(gt_ins))
            # for labels the number of colours is the number of classes in the image
            gt_ins_clrs = get_colour_count(gt_ins_img)
            gt_data[indx]['gt_instances'] = len(gt_ins_clrs)
            gt_data[indx]['gt_inst_bkg'] = 0
            gt_data[indx]['gt_bkgs_match'] = 0
            #for instances the largest colour is the background
            for item in gt_ins_clrs:
                if gt_data[indx]['gt_inst_bkg'] < gt_ins_clrs[item]:
                    gt_data[indx]['gt_inst_bkg'] = gt_ins_clrs[item]
            if gt_data[indx]['gt_inst_bkg'] == gt_data[indx]['gt_background']:
                gt_data[indx]['gt_bkgs_match'] = 1
        if pr_lbl.exists() and pr_lbl.is_file():
            pr_lbl_img = plt.imread(str(pr_lbl))
            # for labels the number of colours is the number of classes in the image
            pr_lbl_clrs = get_colour_count(pr_lbl_img)
            gt_data[indx]['pr_classes'] = len(pr_lbl_clrs)
            for color in label_colors:
                clr_indx = label_colors[color][0]+(1.0,)
                tag = "pr_"+label_colors[color][1]
                gt_data[indx][tag] = 0
                if(clr_indx in pr_lbl_clrs):
                    gt_data[indx][tag] = pr_lbl_clrs[clr_indx]
        if pr_ins.exists() and pr_ins.is_file():
            pr_ins_img = plt.imread(str(pr_ins))
            # for labels the number of colours is the number of classes in the image
            pr_ins_clrs = get_colour_count(pr_ins_img)
            gt_data[indx]['pr_instances'] = len(pr_ins_clrs)
            gt_data[indx]['pr_inst_bkg'] = 0
            gt_data[indx]['pr_bkgs_match'] = 0
            #for instances the largest colour is the background
            for item in pr_ins_clrs:
                if gt_data[indx]['pr_inst_bkg'] < pr_ins_clrs[item]:
                    gt_data[indx]['pr_inst_bkg'] = pr_ins_clrs[item]
            if gt_data[indx]['pr_inst_bkg'] == gt_data[indx]['pr_background']:
                gt_data[indx]['pr_bkgs_match'] = 1
        #calculate class differences
        average_diff = 0
        class_count = 0
        for color in label_colors:
            class_name = label_colors[color][1]
            gt_tag = "gt_"+class_name
            pr_tag = "pr_"+class_name
            diff_tag = "cls_diff_"+class_name
            gt_data[indx][diff_tag] = get_mean_area_diff(
                gt_data[indx][gt_tag],gt_data[indx][pr_tag])
            if gt_data[indx][diff_tag] != 0:
                class_count += 1
            average_diff += gt_data[indx][diff_tag]
        gt_data[indx]['cls_diff_avg'] = average_diff/class_count
        #calculate instance count differences
        gt_data[indx]['ins_count_diff'] = abs(gt_data[indx]['gt_instances']-gt_data[indx]['pr_instances'])

        if indx == 10:
            break
                                              
# writes csv data to the given file name
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


# ground truth dataset
def get_gt_values(argv,label_colors=None):
    print('Arguments:', argv)
    try:
        gt_path = argv[0]
        pr_path = argv[1]
        out_file = argv[2]
    except:
        print("provide three arguments:"+
              "\n -string ground truths path\n -string predictions path"+
              "\n -string output filename (csv)")
        return
    gt_dir= Path(gt_path)
    # predictions dataset
    pr_dir = Path(pr_path)

    images_dir = gt_dir / 'images'
    labels_dir = gt_dir / 'labels'
    instances_dir = gt_dir / 'instances'

    images_list = test_files_list(images_dir,8,2)
    #print (images_list)
    i=1
    data_from_files = {}
    # get file names
    for file_path in images_list:
        file_name = file_path.name
        file_name[:-4]+"_labels.png"
        data_from_files[i] = {"image":file_name,"labels":file_name[:-4]+"_labels.png","instances":file_name[:-4]+"_instances.png"}
        i+= 1
    #print(data_from_files)
    read_gt_data(labels_dir, instances_dir, pr_dir, data_from_files,label_colors)
    out_file = pr_dir / out_file
    write_csv_data(data_from_files, out_file)

if __name__ == "__main__":
   label_colors = {1:[(0.0,0.0,0.0),'background'],2:[(1.0,1.0,1.0),'barcode'],
                3:[(1.0,0.0,0.0),'label'],4:[(1.0,1.0,0.0),'specimen'],
                5:[(0.0,0.0,1.0),'typelabel']}
   get_gt_values(sys.argv[1:], label_colors)
