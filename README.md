# Verifications of ground truth images

The purpose of the scripts in this repository is to Verify that the ground truth classes and instances are valid before using them for training, testing and validation.

The repository also contains scripts to prepare images for training and validation. The scripts are intended to produce homogeneous training sets by cutting, scaling and rotating the images.

## Data preparation scripts
Scripts to transform datasets (resize, extend, cut)
* processgti directory contains two python libraries wich have images processing functions which strech, cut and rezise images in preparation for training
* crop_sample.py is an script for cutting the slides and herbarium sheet images, making them all the size required for training
* herbarium_correct.py, herbarium_correct_hsk.py, herbarium_correct_ldn.py, herbarium_correct_scales.py, herbarium_gtiv.py, herbarium_prepare_unlabelled.py, herbarium_segments.py, herbarium_verify.py, herbarium_verify2.py, herbariumchangebkg.py,
herbariumnotsegmented.py, herbariumt72dpitest.py: files used to process herbarium sheet files, including verification of ground truths matching of labels and instance areas.
* notused.py: copies unused files to a new directory by reading the list of files in a labelled set directory and compare them to the list of files on a download set directory.
* randomsampleused.py: Verify if files in directory have been used for training Need training dataset directory and samples directory as input non used files will be copied to a sub directory under samples
* slide_segments.py, slide_verify.py, slide_verify2.py, slidesnotsegmented.py: Preprocessing and verification of microscopy slides sets before training


## Results validation scripts
Scripts to verify instance-classes ground truths
* countcolur.py and coutcolours.py are used to compare the results of the segmentation against the ground truths. They generate a csv file with tru positives, false positives, true negatives and false negative files
* pre_analysis.py compare gt to predictions to determine confusion matrixes values
* read_data_values.py: early version of prediction analysis


## Yolo scripts
Scripts to generate YOLO (and RCNN) labels

* get_yolo_gt.py and get_yolo_gt2.py are used to generate the gt.csv file which contains the coordinates of each instance in a file from the groundtruths. it read each instance file, gets the idividual poligons and then reads the 
corresponding class file to assing the corresponding class (as a colour) 
* yolo files.ipynb a notebook that generates the txt anotation files required for training YOLO V3

Jupyter notebooks for testing YOLO V3

* Custom_OD.ipynb a notebook that trains YOLO V3 for custom object detection
* TestYoloV3woPoetry.ipynb a notebook to use CV2 to thest the object detector trained with Custom_OD.ipynb

## other files
The scripts used to test different ways of doing things

* graph_paths.py and graph_sets.py are used to test the reading of paths from a set of coordinate points. These were used as the basis to create count colour and get yolo scripts
iterate_tools.py  dummy code for testing iterators a
* read_img.py: testing use of CV2 for reading and showing images
* seed_test_set.py: for testing detection using matlab functions
* SpeedUpCalcs.ipynb notebook testing alternatives to speed up the comparison of grounf truths to segmentation results


## Funding
The main funding for this work came from the ICEDIG project.
ICEDIG – “Innovation and consolidation for large scale digitisation of natural heritage” H2020-INFRADEV-2016-2017 – Grant Agreement No. 777483
