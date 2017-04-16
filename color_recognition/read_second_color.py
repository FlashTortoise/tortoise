import numpy as np
import cv2
import glob
import os
import color_detect as ct
# Change the current working directory to path containing pics
os.chdir(r"D:/TDPS/data/sunny_color_square3_blue")
# get names of pic files
name = glob.glob("*.jpg")
# get paths of pic files
for pic_name in name:
    srcPath = pic_name
    path = os.path.abspath(srcPath)
    print srcPath
    # print path
    # get image of pics
    im = cv2.imread(path)
    im_hsv = im_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    boundaries_red = [([125, 60, 46], [153, 255, 255])]
    boundaries_blue = [([100, 80, 46], [124, 255, 255])]
    boundaries_green = [([20, 60, 46], [70, 255, 255])]
    mask, im_object, contours = ct.color_track(
        im_hsv, boundaries_blue)
    location, area, contours_find = ct.color_location(im_hsv, contours)
    print location
    im_object = cv2.cvtColor(im_object, cv2.COLOR_HSV2BGR)
    im_contours = cv2.drawContours(
        im_object, [contours_find], -1, (0, 0, 255), thickness=cv2.FILLED)

    cv2.circle(im_contours, location, 63, (255, 0, 0))
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image',im_contours)
    if ct.stop_check(area) == 1:
        print 'stop'
        # break
    print area
    while cv2.waitKey(0) != 27:
        pass
    cv2.destroyAllWindows()