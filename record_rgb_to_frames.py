from threading import Thread
import threading
import cv2
import time
import os
import argparse
import csv
import time
from utils.helpers import make_clean_folder, Annotation, TimeTracker

## for 15 fps
# height = 720
# width = 1280

## for 15 fps
height = 540
width = 960

# frame_rate = 20  # frame rate for making video


def make_clean_folder(path_folder):
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)

def record_frame(cap, frame_dir, annot_path, run_event):

    time.sleep(1)

    # for a given id, only 1 annotation file needed
    annotator = Annotation(os.path.dirname(frame_dir))
    time_tracker = TimeTracker()

    frame_count = 0

    start_time = time.time()

    while run_event.is_set():

        try:
            ret, frame = cap.read()

            if ret:
                
                img_name = str(frame_count).zfill(6) + '.png'
                img_path = os.path.join(frame_dir, img_name)

                cv2.imwrite(img_path, frame)

                # # get time
                # curr_time = time.time() - start_time
                # curr_time = round(curr_time % 10000, 2)

                annotator.update(img_name)
                time_tracker.update()

                # # save annot
                # with open(annot_path, 'a') as f:
                #     write = csv.writer(f)
                #     write.writerow([frame_count, curr_time])                    

                # time.sleep(.01)
                frame_count += 1

        except Exception as e:

            print(e)
            print('some kind of error')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='record videos to frames for rgb/depth cameras')
    parser.add_argument('--out_dir', default='.', help='path to output images')
    parser.add_argument('--cam_nums', type=int, nargs='+', help='num of rgb cams to use, takes in a list of ints')
    args = parser.parse_args()

    # video_writers = []
    frame_dirs = []
    caps = []
    annot = []

    for cam_num in args.cam_nums:

        # create new dir
        cam_dir = os.path.join(args.out_dir, str(cam_num))
        make_clean_folder(cam_dir)

        # # create video writer and path
        # out_path = os.path.join(out_dir, 'video{}.mp4'.format(str(cam_num)))
        # video_writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, (width, height), 1)
        # video_writers.append(video_writer)

        frame_dir = os.path.join(cam_dir, 'color')
        make_clean_folder(frame_dir)
        frame_dirs.append(frame_dir)
        
        # open camera
        cap = cv2.VideoCapture(cam_num)
        caps.append(cap)

        # create annotator
        annot_path = os.path.join(cam_dir, 'annotation.csv')

        # fields = ['frame_num', 'time'] 

        # # create an annotator
        # with open(annot_path, 'w') as f:
        #     write = csv.writer(f)
        #     write.writerow(['start time', time.time()])
        #     write.writerow(fields)

        annot.append(annot_path)


    # for multithreading
    run_event = threading.Event()
    run_event.set()

    threads = []

    # start threads
    for t in range(len(args.cam_nums)):
        thr = Thread(target=record_frame, args=(caps[t], frame_dirs[t], annot[t], run_event))
        threads.append(thr)
        thr.daemon = True
        thr.start()

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:

        run_event.clear()

        for i, thr in enumerate(threads):
            thr.join()
            caps[i].release()
        
        print("threads successfully closed")

    print('done!')



'''

python ~/Desktop/footprints/record_rgb_to_frames.py --out_dir ~/Desktop/testing_videos/run8 --cam_nums 0

'''


