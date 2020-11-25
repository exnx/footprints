from threading import Thread
import threading
import cv2
import time
import os
import argparse
import csv
import time


height = 720
width = 1280
frame_rate = 20  # frame rate for making video


def make_clean_folder(path_folder):
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)

def record_frame(cap, video_writer, annot_path, run_event):

    frame_count = 0

    start_time = time.time()

    while run_event.is_set():

        try:
            ret, frame = cap.read()

            if ret:
                video_writer.write(frame)

                # get time
                curr_time = time.time() - start_time
                curr_time = round(curr_time % 10000, 2)

                # save annot
                with open(annot_path, 'a') as f:
                    write = csv.writer(f)
                    write.writerow([frame_count, curr_time])                    

                time.sleep(.01)
                frame_count += 1

        except Exception as e:

            print(e)
            print('some kind of error')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='record videos to frames for rgb/depth cameras')
    parser.add_argument('--out_dir', default='.', help='path to output images')
    parser.add_argument('--cam_nums', type=int, nargs='+', help='num of rgb cams to use, takes in a list of ints')
    args = parser.parse_args()

    video_writers = []
    caps = []
    annot = []

    for cam_num in args.cam_nums:

        # create new dir
        out_dir = os.path.join(args.out_dir, str(cam_num))
        make_clean_folder(out_dir)

        # create video writer and path
        out_path = os.path.join(out_dir, 'video{}.mp4'.format(str(cam_num)))
        video_writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, (width, height), 1)
        video_writers.append(video_writer)
        
        # open camera
        cap = cv2.VideoCapture(cam_num)
        caps.append(cap)

        # create annotator
        annot_path = os.path.join(out_dir, 'annot{}.csv'.format(str(cam_num)))

        fields = ['frame_num', 'time'] 

        # create an annotator
        with open(annot_path, 'w') as f:
            write = csv.writer(f)
            write.writerow(['start time', time.time()])
            write.writerow(fields)

        annot.append(annot_path)


    # for multithreading
    run_event = threading.Event()
    run_event.set()

    threads = []

    # start threads
    for t in range(len(video_writers)):
        thr = Thread(target=record_frame, args=(caps[t], video_writers[t], annot[t], run_event))
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

python two_cam_thread_with_time.py --out_dir ~/Desktop/testing_videos/run2 --cam_nums 0 1

'''


