import cv2
import numpy as np
import pyrealsense2 as rs
import os
import argparse
import threading
from threading import Thread
import time
import csv
from utils.helpers import Annotation, TimeTracker, make_clean_folder
import concurrent.futures


####  Constants  #####
######################

frame_rate = 30

# for 20 fps
# color_height = 720
# color_width = 1280

# for 30 fps
color_height = 540
color_width = 960


depth_height = 360
depth_width = 640

#######################



def config_rs_cameras(rs_cam_ids):

    '''
    Configures cameras by id, returns a list of for each camera parameter

    '''

    pipelines = []
    aligns = []
    depth_scales = []

    for cam_id in rs_cam_ids:

        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device(cam_id)  # optional for 1 cam only

        # format is w, h
        config.enable_stream(rs.stream.depth, depth_width, depth_height, rs.format.z16, frame_rate)
        config.enable_stream(rs.stream.color, color_width, color_height, rs.format.bgr8, frame_rate)

        profile = pipeline.start(config)

        depth_sensor = profile.get_device().first_depth_sensor()
        # depth_sensor.set_option(
        #     rs.option.visual_preset, 3
        # )  # Set high accuracy for depth sensor
        depth_scale = depth_sensor.get_depth_scale()

        # clipping_distance_in_meters = 1
        # clipping_distance = clipping_distance_in_meters / depth_scale

        align_to = rs.stream.color
        align = rs.align(align_to)

        pipelines.append(pipeline)
        aligns.append(align)
        depth_scales.append(depth_scale)

    return pipelines, aligns, depth_scales


def make_cam_dirs(out_dir, rs_id):

    '''
    Makes a dict with two key: vals, for depth and color directory paths

    '''

    # make a cam dir
    cam_path = os.path.join(out_dir, rs_id)

    # make depth dir path
    depth_dir_path = os.path.join(cam_path, 'depth')
    make_clean_folder(depth_dir_path)
    
    # make color dir path
    color_dir_path = os.path.join(cam_path, 'color')
    make_clean_folder(color_dir_path)

    return depth_dir_path, color_dir_path



def save_frame(img_id_num, cam_dirs, annotator, pipeline, align, depth_scale):

    depth_dir_path = cam_dirs[0]
    color_dir_path = cam_dirs[1]

    try:

        # get frames
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            raise

        # convert to np
        color_image = np.asarray(color_frame.get_data())
        depth_image = np.asarray(depth_frame.get_data())

        # id bookeeping
        img_id = str(img_id_num).zfill(6)
        img_name = img_id + '.png'

        # prep for saving
        depth_path = os.path.join(depth_dir_path, img_name)
        color_path = os.path.join(color_dir_path, img_name)

        # save images and annotations
        cv2.imwrite(depth_path, depth_image.astype(np.uint16))
        cv2.imwrite(color_path, color_image)

        annotator.update(img_name)

    except Exception as e:

        print(e)
        print('some kind of error')



def main(args):

    ### comment this on/off to get the seial numbers of the Realsense cams
    # ctx = rs.context()
    # devices = ctx.query_devices()

    # # start realsense cameras
    # for device in devices:
    #     print('device', device)

    # print(devices)
    # exit()
    ###

    # check if out_dir exists, if so, keep appending a new suffix
    count = 1
    out_dir = args.out_dir

    while os.path.exists(out_dir):
        out_dir = args.out_dir + '_v{}'.format(count)
        count += 1

    rs_cam_ids = args.cams

    # configure rs cameras (return list of pipelines and alignment objects)
    pipelines, aligns, depth_scales = config_rs_cameras(rs_cam_ids)


    print('about to start threads')

    all_cam_dirs = []
    annotators = []

    # get annotators and cam dirs for each camera
    for rs_id in rs_cam_ids:
        # create dirs for this camera (for frames)
        depth_dir_path, color_dir_path = make_cam_dirs(out_dir, rs_id)
        all_cam_dirs.append((depth_dir_path, color_dir_path))

        annotator = Annotation(os.path.join(out_dir, rs_id))
        annotators.append(annotator)

    time.sleep(1)  # make sure cameras are all initialized
    time_tracker = TimeTracker()

    img_id_num = 0  # for frame names (same id across all cams)

    try:
        while True:
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = []

                # create threads to read / write a single frame for each cam, continuously
                for i in range(len(rs_cam_ids)):
                    futures.append(executor.submit(save_frame, img_id_num, all_cam_dirs[i], annotators[i], pipelines[i], aligns[i], depth_scales[i]))

                # make sure all frames are done to ensure time synchronozation
                finished, pending = concurrent.futures.wait(futures, timeout=None, return_when=concurrent.futures.ALL_COMPLETED)

                img_id_num += 1
                time_tracker.update()

    except KeyboardInterrupt:
        print('keyboard interupt, all DONE!')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='record videos to frames for rgb/depth cameras')
    parser.add_argument('--out_dir', help='path to output images')
    parser.add_argument('--cams', nargs='+', default=['032622073591', '032622070525', '032622071103', '844212071513'])

    args = parser.parse_args()

    main(args)




'''

python ~/Desktop/footprints/record_realsense_to_frames_rev1.py --out_dir ~/Desktop/testing_videos/run12 --cams 032622071103


'''





