Pipeline for creating the footsteps dataset


For examples to run each script, see the bottom of each script.


use conda environment, on Windows Alienware machine, use:

`conda activate py37`

requires `opencv-contrib` version for Aruco marker detection





1) Record from Realsense RGB-D cameras

`record_realsense_to_frames.py`

flags
--out_dir:  where to output the frames

optional
--cams:  serial codes for each individual camera, otherwise will use all

description:  this will record the realsense rgb-d cameras on separate threads.  It will create annotations with timestamps 
for each frame collected on each camera, in their respective camera id directories.



1a) Record with RGB cameras

`record_rgb_to_frames.py`

flags
--out_dir:  where to output the frames

optional
--cam_nums:  the usb cam number, e.g., 0, 1, 2

description:  this will record the rgb cameras on separate threads.  It will create annotations with timestamps 
for each frame collected on each camera, in their respective camera id directories.



2) get foot detections on rgb and create masks

`detect_from_frames.py`

flags
input_dir:  path to the color frames of the camera pointing at the shoes

optional
output_dir:  output path, otherwise, will go to same parent dir of input frames

description:  this will take the color frames and detect the aruco markers, and create masks in a separate directory.



3) apply masks to rgb frames (optional)

`apply_mask_on_rgb.py`

flags
img_dir: must input the path to the color frames to be used
mask_dir: must input the path to the mask frames to be used

optional
output_dir:  output path, otherwise, will go to same parent dir of (color) img frames

description:  this will take the color frames and apply the masks on top, to created masked images.



4) create videos from frames (optional)

`frames_to_videos.py`

flags:
run_dir:  path to the successful run to collect frames.  

description:  this will search for directories with frames and create videos.  It will make videos for color, depth, masks, masked frames.




