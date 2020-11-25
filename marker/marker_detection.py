import numpy as np
import cv2
import cv2.aruco as aruco
import glob
import math
import socket
import os
import argparse
import tqdm



class Calibrate:

    def calibrate(self, directory):

        width = 9
        height = 6

        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((height*width,3), np.float32)
        objp[:,:2] = np.mgrid[0:width,0:height].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.

        images = glob.glob('{}/*.jpg'.format(directory))

        # reads image in dir
        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (width,height),None)

            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)

                corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
                imgpoints.append(corners2)

                # Draw and display the corners
                img = cv2.drawChessboardCorners(img, (width,height), corners2, ret)  

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

        return (mtx, dist, rvecs, tvecs)


class MarkerDetection:

    def __init__(self, calibration_dir=None):

        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
        self.parameters = aruco.DetectorParameters_create()

    def detect_markers(self, frame, draw=False):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #lists of ids and the corners beloning to each id
        markers, ids, rejectedImgPoints = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

        return markers


    def in_bounds(self, up_points, height, width):

        adjusted_points = []

        out_bounds_count = 0

        # loop thru np array
        for x, y in up_points:

            # height
            if x < 0:
                new_x = 0
                out_bounds_count += 1
            elif x > width:
                new_x = width
                out_bounds_count += 1
            else:
                new_x = x

            if y < 0:
                new_y = 0
                out_bounds_count += 1
            elif y > height:
                new_y = height
                out_bounds_count += 1
            else:
                new_y = y

            adjusted_points.append([new_x, new_y])

        # if all points are out of bound, then return None
        if out_bounds_count == 4:
            return None

        return adjusted_points


    def adjust_up(self, marker, height, width):

        MOVE_FACTOR = 1.75 # move all points by 1.5x of marker height in front (up)

        points = marker[:]  #

         # sort by second element (columns) to find the left most points
        sorted_points = sorted(points.tolist(), key=lambda x: x[1]) 

        # get left points
        left_points = sorted_points[:2]

        try:
            p1, p2 = left_points

        except Exception as e:
            print('stuck')

        # points are given in x, y, where x is horizontal axis, y is the vertical
        # not rows and column coordinates! Confusing
        rise = abs(p2[0] - p1[0])
        runn = abs(p2[1] - p1[1])

        # move the points up
        up_points = marker + MOVE_FACTOR * np.asarray([0, -rise])  # array subtraction to move upward

        up_points = up_points.tolist()

        # need to make sure all are in bounds, returns None if new points are all out of bounds
        adjusted_points = self.in_bounds(up_points, height, width)

        if adjusted_points is not None:
            return np.asarray(adjusted_points)

        # if new marker is out of bounds, return None
        return None






















