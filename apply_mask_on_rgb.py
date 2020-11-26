import cv2
import numpy as np
import os
import argparse
import glob


def make_clean_folder(path_folder):
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)

def main(args):
    img_list = glob.glob('{}/*.png'.format(args.img_dir))
    img_list.sort()
    mask_list = glob.glob('{}/*.png'.format(args.mask_dir))

    # place masked imgs in same parent dir of rgb imgs
    up_dir_name = os.path.dirname(args.img_dir)
    out_dir_path = os.path.join(up_dir_name, 'masked')
    make_clean_folder(out_dir_path)

    print('creating masked images...')

    # loop thru images
    for i in range(len(img_list)-1):

        if i % 100 == 0:
            print('{} masked images completed'.format(i))

        img_path = img_list[i]
        file_name = os.path.basename(img_path)
    
        img = cv2.imread(img_path)

        mask_path = os.path.join(args.mask_dir, file_name)     
        mask = cv2.imread(mask_path)

        try:
            masked_img = cv2.bitwise_or(img, mask)
        except:
            print('could not apply')
            import pdb; pdb.set_trace()

        out_path = os.path.join(out_dir_path, file_name)
        cv2.imwrite(out_path, masked_img)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='run object detection')
    parser.add_argument('--img_dir', help='path to dir of input imgs')
    parser.add_argument('--mask_dir', help='path to dir of mask imgs')
    args = parser.parse_args()

    main(args)


'''

python ~/Desktop/footprints/apply_mask_on_rgb.py --img_dir ~/Desktop/footprints_preds/color3_frames --mask_dir ~/Desktop/footprints_preds/color3_pred_adjusted3/mask

'''






