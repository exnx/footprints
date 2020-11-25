import argparse
import glob
import os
import cv2
from utils.helpers import make_clean_folder

######## constants #####

frame_rate = 30  # this may need to change if the cam had reduced frame rate (rgb)

########################


def create_video(img_dir, img_type, colorize=False):

    print('writing video for:', img_dir)

    # get list of depth imgs
    imgs = glob.glob(os.path.join(img_dir, '*.png'))
    imgs.sort()

    if colorize:
        suffix = '_colorize'
    else:
        suffix = ''

    video_name = img_type + suffix + '.mp4'

    dir_up_path = os.path.dirname(img_dir)  # write video up one level from its frames
    writer_path = os.path.join(dir_up_path, video_name)

    # get img height x width
    img = cv2.imread(imgs[0])
    height, width = img.shape[:2]  # only grab first 2, since it's variable

    writer = cv2.VideoWriter(writer_path, cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, (width, height), 1)
  
    # loop thru paths, open and convert
    for img_path in imgs:

        # import pdb; pdb.set_trace()

        if img_type != 'mask':
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)  # need flag to keep np.unint16 format
        else:
            img = cv2.imread(img_path)  # need to allow for 3 channel for mask

        if colorize:
            img = cv2.applyColorMap(cv2.convertScaleAbs(img, alpha=0.03), cv2.COLORMAP_JET)

        writer.write(img)

    writer.release()


def main(args):

    # get all subdirs for each cam
    cam_dirs = glob.glob(args.run_dir + '/*')

    # find depth and color frame dirs for this cam
    for cam_dir in cam_dirs:

        depth_dir = os.path.join(cam_dir, 'depth')
        color_dir = os.path.join(cam_dir, 'color')
        mask_dir = os.path.join(cam_dir, 'mask')
        masked_dir = os.path.join(cam_dir, 'masked')

        if os.path.exists(depth_dir):
            create_video(depth_dir, 'depth', True)

        if os.path.exists(color_dir):
            create_video(color_dir, 'color', False)

        if os.path.exists(mask_dir):
            create_video(mask_dir, 'mask', False)

        if os.path.exists(masked_dir):
            create_video(mask_dir, 'masked', False)


if __name__ == "__main__":


    parser = argparse.ArgumentParser(description='create videos from color and depth frames')
    parser.add_argument('--run_dir', help='path to directory of a successful run')

    args = parser.parse_args()

    main(args)



'''

python ~/Desktop/footprints/frames_to_videos.py --run_dir ~/Desktop/testing_videos/run8



run_dir = path to the successful run.  Each dir will have multiple camera ids, and within each id, there
will be a depth and color dir of frames.

file structure example

run1   <-- pass this path
    cam_id
        color
        depth
    cam_id
        color
        depth

run2
    cam_id
        color
        depth

'''


