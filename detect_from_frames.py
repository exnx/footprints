import numpy as np
import cv2
import cv2.aruco as aruco
# from cv2 import aruco
import glob
import math
import socket
import os
import argparse
import tqdm
import csv
from matplotlib.path import Path  # for making binary mask
import pylab as plt
from PIL import Image
from marker.marker_detection import MarkerDetection


def make_dir(path):

    if not os.path.exists(path):
        os.makedirs(path)
    return


def save_mask(mask, img_name1, save_dir):
    
    '''

    input: a binary mask of booleans, single channel
    saves mask (of booleans) as a png

    '''

    outname = os.path.splitext(img_name1)[0] + '.png'
    outpath = os.path.join(save_dir, outname)

    mask.save(outpath)

    return outpath


def create_masks_using_markers(frame, markers_in_frame):

    '''

    take in a frame, and markers from a variable number of frames in the future,
    and inprint all markers onto the frame as a mask

    argv:  list of markers for a single img, each with a list of markers themselves

    '''
    ny, nx = frame.shape[0], frame.shape[1]

    x, y = np.meshgrid(np.arange(nx), np.arange(ny))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x,y)).T

    image_mask = np.zeros([ny, nx])
    grids = []

    # loop thru all markers and create polygons
    # for marker_set in markers_in_frame:
    for marker in markers_in_frame:

        marker = marker.astype('int32')

        path = Path(marker)
        grid = path.contains_points(points)
        grid = grid.reshape((ny, nx))
        grids.append(grid)

    # loop thru polygons and accumulate them on a single image
    for grid in grids:
        image_mask = np.logical_or(image_mask, grid) 

    im = Image.fromarray(image_mask).convert("L")

    return im


def save_annotations(img_outpath, mask_outpath, markers1, annotations_path):

    if not os.path.exists(annotations_path):
        with open(annotations_path, 'w', newline='') as csvfile:
            fieldnames = ['img_path', 'mask', 'bbox', 'has_foot']
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(i for i in fieldnames)

    try:
        with open(annotations_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

            # boxes
            boxes = []
            
            for i in range(len(markers1)):
                boxes.extend(markers1[i])

            if len(boxes) > 0:
                has_foot = True
            else:
                has_foot = False

            writer.writerow([os.path.basename(img_outpath), os.path.basename(mask_outpath), boxes, has_foot])

        return True

    except Exception as e:

        print(e)

        return False


def main(args):

    if not args.output_dir:
        output_dir = os.path.dirname(args.input_dir)
    else:
        output_dir = args.output_dir

    mask_dir = os.path.join(output_dir, 'mask')
    make_dir(mask_dir)

    # create csv
    annotations_path = os.path.join(output_dir, 'mask_annotation.csv')

    # start with detection markers (as the foot)
    marker_det = MarkerDetection()

    # get list of images
    image_list = glob.glob('{}/*.png'.format(args.input_dir))

    image_list.sort()

    print('creating masks...')

    # loop thru until len-1, starting with 2nd img
    for i in range(len(image_list)):

        if i % 100 == 0:
            print('{} masks completed'.format(i))

        img_name1 = os.path.basename(image_list[i])
        img_path1 = os.path.join(args.input_dir, img_name1)
        frame1 = cv2.imread(img_path1)
        markers1 = marker_det.detect_markers(frame1)

        # adjust markers here
        markers1_adj = []
        for marker in markers1:
            # returns None if adjusted marker is out of bounds
            adj_marker = marker_det.adjust_up(marker[0], frame1.shape[0], frame1.shape[1])

            # if new marker is in bounds, add
            if adj_marker is not None:
                markers1_adj.append(adj_marker)

            markers1 = markers1_adj

        # create binary mask for each marker
        # print('creating make for  {}, and {}'.format(img_name1, img_name2))
        mask1 = create_masks_using_markers(frame1, markers1)

        mask_outpath = save_mask(mask1, img_name1, mask_dir)

        # create csv with annotations
        rt = save_annotations(img_path1, mask_outpath, markers1, annotations_path)

        if not rt:
            print('annotation not saved...!')
            break


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='run object detection')
    parser.add_argument('--input_dir', help='path to dir of frames')
    parser.add_argument('--output_dir', default='', help='path to dir of output, will default to same as input dir parent')

    args = parser.parse_args()

    main(args)



'''

python ~/Desktop/footprints/detect_from_frames.py --input_dir ~/Desktop/testing_videos/run6_v1/032622071103/color


Note:  output_dir by default goes to same (parent) dir as the input_dir

'''


