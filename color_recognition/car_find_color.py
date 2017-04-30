import glob
import os
from collections import namedtuple

import cv2
import numpy as np

import tortoise as t
from tortoise import config

import color_detect as ct

SIGHT_PIXEL_COUNT = (config.EYE_SIGHT_HEIGHT * config.EYE_SIGHT_WIDTH)
EXPECTED_BLOCK_AREA = 20000
HALF_WIDTH = config.EYE_SIGHT_WIDTH / 2

def imgs(path):
    path = os.path.expanduser(path)
    yield cv2.imread(pic_path)
    for pic_path in glob.iglob(path):

        t.update_config(
             EYE_SIMULATOR_ACTIVE=True,
             EYE_SIMULATOR_DATASET=imgs(r'D:/TDPS/data/sunny_color_square1_red/*.JPG')
         )


#t.update_config(TORTOISE_WALK_PERIOD=1)

eye = t.peripheral.eye


class ColorTracingTask(t.Task):

    def __init__(self):
        super(ColorTracingTask, self).__init__()

        self.find_task = FindBlockTask()

    def step(self):
        self.find_task.step()

        print 'speed: %5.3f direction: %8.1f' % (
            self.find_task.speed, self.find_task.direction)


class FindBlockTask(t.Task):

    def __init__(self):
        super(FindBlockTask, self).__init__()

        self.found = False
        self.speed = 0
        self.direction = 0
        self.stop = 0

        self.rec = t.get_recorder('block_following')
        self.color_index = 0
        # color index is going to denote the times that the color is recorded
        self.if_color_found = False
        self.color = ([0, 0, 0], [0, 0, 0])

    def step(self):

        im = eye.see()
        im_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        boundaries_red = [([125, 80, 46], [153, 255, 255])]
        boundaries_blue = [([100, 100, 46], [124, 255, 255])]
        boundaries_green = [([20, 60, 46], [46, 255, 255])]

        if self. if_color_found == False:
            # if the color not found, track three colors in the img
            _, im_object, contours = ct.multi_color_track(
                im_hsv, boundaries_red, boundaries_green, boundaries_blue)
        else:
            # if the color is found, only track one color in the img
            _, im_object, contours = ct.color_track(im_hsv, self.color)

        location, _, area, contours_find = ct.color_location(
            im_hsv, contours)

        detect_color = ct.get_color(
            contours_find, im_hsv, boundaries_red, boundaries_green, boundaries_blue)

        if area < 100:

            print 'area too small, color not found'
            self.set_not_found()
            return

        else:

            self.found = True

            if self.if_color_found == False:
                self.color = self. color_check(area)

            self.stop = ct.stop_check(area)

            if self.stop == 1:

                # case: the car should stop since it arrive the block
                print 'tortoise stop'
                self.speed = 0
                self.direction = 0
                return

            else:

                if location[0] < config.EYE_SIGHT_WIDTH * 0.1 + 5:

                    # case: the car should turn big left
                    print 'turn big left'
                    self.speed = 0
                    self.direction = -30
                    return

                elif location[1] > config.EYE_SIGHT_WIDTH * 0.9 - 5:
                    # case: the car should turn right
                    print 'trun big right '
                    self.speed = 0
                    self.dirction = 30
                    return

                else:

                    self. speed = 0
                    self.dirction = float(
                        (location[0] - HALF_WIDTH)) / HALF_WIDTH * 10

    def set_not_found(self):
        self.found = False
        self.direction = 0
        self.speed = 0

    def color_check(self, area):

        if self.color_index == 0:
            boundary_mat = []

        if self.color_index >= 4:

            a_01 = boundary_mat[0] == boundary_mat[1]
            a_23 = boundary_mat[2] == boundary_mat[3]
            a_02 = boundary_mat[0] == boundary_mat[2]
            a_04 = boundary_mat[0] == boundary_mat[4]
            self.color_index = 0

            if a_01 == 1 and a_23 == 1 and a_02 == 1 and a_04 == 1:
                self.if_color_found = True
                return boundary_mat[0]
            else:
                self.if_color_found = False
                return boundary_mat[0]

        else:
            boundary_mat.append(area)
            self.color_index = self.color_index + 1
            self.if_color_found = False
            return boundary_mat[0]


if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = ColorTracingTask()
    tttt.walk()