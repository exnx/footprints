Pipeline for creating the footsteps dataset

Data collected on Nov 25, 2020 is on the Desktop of the Alienware laptop under `new_videos`.



For examples to run each script, see the bottom of each script.


use conda environment, on Windows Alienware machine, use:

`conda activate py37`

requires `opencv-contrib` version for Aruco marker detection, as well as Pysense (the Realsense library for Python).
See online for how to install these, or just the default environment above.

Note, on Windows Alienware, you need to use the Anaconda Prompt specifically.  ie, in the search menu bottom left, type Anaconda, and select the Anaconda Prompt.  You can then activate the environment as usual and run the scripts.





1) Record from Realsense RGB-D cameras

`record_realsense_to_frames.py`

flags
--out_dir:  where to output the frames

optional
--cams:  serial codes for each individual camera, otherwise will use all

description:  this will record the realsense rgb-d cameras on separate threads.  It will create annotations with timestamps 
for each frame collected on each camera, in their respective camera id directories.

windows example:
`python record_realsense_to_frames.py --out_dir C:\Users\GuibasLab\Desktop\tmp_videos\run1`




2) get foot detections on rgb and create masks

`detect_from_frames.py`

flags
input_dir:  path to the color frames of the camera pointing at the shoes

optional
output_dir:  output path, otherwise, will go to same parent dir of input frames

description:  this will take the color frames and detect the aruco markers, and create masks in a separate directory.  Note, each run only has 1 camera that has detectable footprints.  So you'll need to find this folder (using color frames) for each run, but likely the camera serial number will be the only thing that changes.  So use the command line below, just changing the run number. e.g., run1, run2, run3 etc.

windows example:
python detect_from_frames.py --input_dir C:\Users\GuibasLab\Desktop\new_videos\run3\032622073591\color




3) apply masks to rgb frames (optional)

`apply_mask_on_rgb.py`

flags
img_dir: must input the path to the color frames to be used
mask_dir: must input the path to the mask frames to be used

optional
output_dir:  output path, otherwise, will go to same parent dir of (color) img frames

description:  Note, you need to first run the detection to create the masks before this step.  Then this will take the color frames and apply the masks on top, to created masked images.

windows example:
python apply_mask_on_rgb.py --img_dir C:\Users\GuibasLab\Desktop\new_videos\run1\032622073591\color --mask_dir C:\Users\GuibasLab\Desktop\new_videos\run1\032622073591\mask



4) create videos from frames (optional)

`frames_to_videos.py`

flags:
run_dir:  path to the successful run to collect frames.  

description:  this will search for directories with frames and create videos.  It will make videos for color, depth, masks, masked frames in the directory of the run (no need to pass output dir).


windows example:
python frames_to_videos.py --run_dir C:\Users\GuibasLab\Desktop\new_videos\run1

