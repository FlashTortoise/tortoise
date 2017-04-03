import glob
import os

import cv2
import numpy as np

import tortoise as t
from tortoise import config


def imgs(path):
    path = os.path.expanduser(path)
    for pic_path in glob.iglob(path):
        yield cv2.imread(pic_path)


t.update_config(
    EYE_SIMULATOR_ACTIVE=True,
    EYE_SIMULATOR_DATASET=imgs('~/Downloads/imgs/*.JPG')
)

eye = t.peripheral.eye


class ColorTracingTask(t.Task):
    def __init__(self):
        super(ColorTracingTask, self).__init__()

        self.find_task = FindBlockTask()

    def step(self):
        self.find_task.step()

        # if find_result.found is True:
        #     self.follow(
        #         dir=find_result.dir,
        #         distance=find_result.distance
        #     )
        # else:
        #     self.follow(dir=0, distance=0)


def extract_info_from_contours(contours):
    def moment2center_of_mass(moment):
        mx = moment['m10'] / moment['m00']
        my = moment['m01'] / moment['m00']
        return mx, my

    weighted_xs, weighted_ys, sum_of_area = [], [], 0
    for contour in contours:
        m = cv2.moments(contour)
        if m['m00'] == 0:
            continue

        a = m['m00']
        x, y = moment2center_of_mass(m)
        weighted_xs.append(x * a)
        weighted_ys.append(y * a)
        sum_of_area += a

    x = sum(weighted_xs) / sum_of_area
    y = sum(weighted_ys) / sum_of_area

    return x, y, sum_of_area


class FindBlockTask(t.Task):
    def __init__(self):
        super(FindBlockTask, self).__init__()

        block_sizes = []
        found = False

    def step(self):
        img = eye.see()
        x, y, area = self.get_block_info(img)

        print x, y, area

    def get_block_info(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img = cv2.inRange(img, (90, 43, 46), (124, 255, 255))
        _, cotrs, _ = cv2.findContours(
            img,
            mode=cv2.RETR_TREE,
            method=cv2.CHAIN_APPROX_SIMPLE
        )

        rtn = x, y, area = extract_info_from_contours(cotrs)
        return rtn


def find_color():
    img = eye.see()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img = cv2.inRange(img, (90, 43, 46), (124, 255, 255))

    _, cotrs, _ = cv2.findContours(
        img,
        mode=cv2.RETR_TREE,
        method=cv2.CHAIN_APPROX_SIMPLE
    )

    x, y, area = extract_info_from_contours(cotrs)

    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    img = cv2.circle(img, (int(x), int(y)), 10, color=(0, 255, 0),
                     thickness=10)

    cv2.drawContours(img, cotrs, -1, color=(0, 0, 255))

    cv2.imshow('img', img)
    cv2.waitKey(0)

    return object()


if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = ColorTracingTask()
    tttt.walk()
