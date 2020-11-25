import os
import csv
import time


def make_clean_folder(path_folder):
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)

class Annotation:

    def __init__(self, out_dir):

        make_clean_folder(out_dir)

        self.annot_path = os.path.join(out_dir, 'annotation.csv')

        fields = ['frame_num', 'time'] 

        self.start_time = time.time()

        with open(self.annot_path, 'w') as f:
            write = csv.writer(f)
            write.writerow(['start time', self.start_time])
            write.writerow(fields)


    def update(self, frame_count):

        curr_time = time.time() - self.start_time
        curr_time = round(curr_time % 10000, 2)

        with open(self.annot_path, 'a') as f:
            write = csv.writer(f)
            write.writerow([frame_count, curr_time])


class TimeTracker:

    def __init__(self):

        self.start_time = time.time()
        self.frame_count = 0
        self.tick = 0

    def update(self):

        self.frame_count += 1

        time_now = time.time() - self.start_time

        # tracks fps
        if time_now - self.tick >= 1:
            self.tick += 1
            print('fps: {}'.format(self.frame_count))
            self.frame_count = 0