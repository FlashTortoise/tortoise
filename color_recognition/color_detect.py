import numpy as np
import cv2
import matplotlib.pyplot as plt


def color_track(im_hsv, boundaries):
        # im_hsv is the image which has been transformed into hsv format
        # find the specified color object
    for (lower, upper) in boundaries:
        lower = np.array(lower)
        upper = np.array(upper)
        mask = cv2.inRange(im_hsv, lower, upper)
        im_object = cv2.bitwise_and(im_hsv, im_hsv, mask=mask)
    # find coutours
    im_gray = cv2.cvtColor(im_object, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(im_gray, 127, 255, cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return (mask, im_object, contours)


def multi_color_track(im_hsv, boundaries_red, boundaries_green, boundaries_blue):

    (mask_red, im_object_red, _) = color_track(im_hsv, boundaries_red)
    (mask_green, im_object_green, _) = color_track(im_hsv, boundaries_green)
    (mask_blue, im_object_blue, _) = color_track(im_hsv, boundaries_blue)
    mask = cv2.add(
        cv2.add(mask_red, mask_blue), mask_green)

    im_object = cv2.add(
        cv2.add(im_object_red, im_object_blue), im_object_green)

    im_gray = cv2.cvtColor(im_object, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(im_gray, 127, 255, cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return(mask, im_object, contours)


def color_location(contours):
    area_list = np.zeros(len(contours))
    i = 0

    for cnt in contours:
        area_list[i] = cv2.contourArea(cnt)
        i = i + 1

    max_ind = np.argmax(area_list)
    max_area = area_list[max_ind]

    # computer the center
    M = cv2.moments(contours[max_ind])
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    max_location = (cx, cy)

    return(max_location, max_ind, max_area, contours[max_ind])
