import glob
import os
from collections import namedtuple

import cv2
import numpy as np

import tortoise as t
from tortoise import config

SIGHT_PIXEL_COUNT = (config.EYE_SIGHT_HEIGHT * config.EYE_SIGHT_WIDTH)
EXPECTED_BLOCK_AREA = 20000
HALF_WIDTH = config.EYE_SIGHT_WIDTH / 2


def imgs(path):
    path = os.path.expanduser(path)
    for pic_path in glob.iglob(path):
        yield cv2.imread(pic_path)


# t.update_config(
#     EYE_SIMULATOR_ACTIVE=True,
#     EYE_SIMULATOR_DATASET=imgs('~/Downloads/imgs/*.JPG')
# )

t.update_config(TORTOISE_WALK_PERIOD=1)

eye = t.peripheral.eye


class ColorTracingTask(t.Task):
    def __init__(self):
        super(ColorTracingTask, self).__init__()

        self.find_task = FindBlockTask()

    def step(self):
        self.find_task.step()

        print 'speed: %5.3f direction: %8.1f' % (
            self.find_task.speed, self.find_task.direction)

        # if find_result.found is True:
        #     self.follow(
        #         dir=find_result.dir,
        #         distance=find_result.distance
        #     )
        # else:
        #     self.follow(dir=0, distance=0)


ContourInfo = namedtuple('ContourInfo', 'area m10 m01')


def extract_info_from_contours(contours, info):
    def info2center_of_mass(ctr_info):
        mx = ctr_info.m10 / ctr_info.area
        my = ctr_info.m01 / ctr_info.area
        return mx, my

    weighted_xs, weighted_ys, sum_of_area = [], [], 0
    for contour, info_piece in zip(contours, info):

        if info_piece.area == 0:
            continue

        a = info_piece.area
        x, y = info2center_of_mass(info_piece)
        weighted_xs.append(x * a)
        weighted_ys.append(y * a)
        sum_of_area += a

    if sum_of_area != 0:
        x = sum(weighted_xs) / sum_of_area
        y = sum(weighted_ys) / sum_of_area
    else:
        x = y = 0

    return x, y, sum_of_area


def contour_size_filter(zipped):
    contour, info = zipped
    return info.area > 0.01 * SIGHT_PIXEL_COUNT


def analyse_contour(contour):
    m = cv2.moments(contour)
    info = ContourInfo(
        area=m['m00'],
        m10=m['m10'],
        m01=m['m01']
    )

    return info


def find_contours(img):
    _, contours, _ = cv2.findContours(
        img,
        mode=cv2.RETR_TREE,
        method=cv2.CHAIN_APPROX_SIMPLE
    )

    return contours


def check_if_block_touch_border(contours, info):
    for contour, info_piece in zip(contours, info):
        if np.any(contour[:, -1, 0] < 5):
            return 'left'
        elif np.any(contour[:, -1, 0] > config.EYE_SIGHT_WIDTH - 5):
            return 'right'

    return False



class FindBlockTask(t.Task):
    def __init__(self):
        super(FindBlockTask, self).__init__()

        self.found = False
        self.speed = 0
        self.direction = 0

        self.rec = t.get_recorder('block_following')

    def step(self):
        img = eye.see()

        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img = cv2.inRange(img, (90, 43, 46), (124, 255, 255))

        contours = find_contours(img)
        info = map(analyse_contour, contours)

        # contours, info = zip(filter(contour_size_filter, zip(contours, info)))
        x, y, area = extract_info_from_contours(contours, info)

        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        cv2.circle(img, (int(x), int(y)), radius=10, color=(255, 255, 0),
                   thickness=10)

        # cv2.imshow('a', img)
        # cv2.waitKey(0)

        if area < 0.01 * SIGHT_PIXEL_COUNT:
            print 'not found'
            self.set_not_found()
            return
        else:
            # There must be a block in sight
            self.found = True

            if area > EXPECTED_BLOCK_AREA:
                print 'Big enough'
                # Case: Block is big enough so that i can grasp it
                self.speed = 0
                self.direction = 0
                return
            else:
                print 'not big enough', int(x), int(y),
                touched = check_if_block_touch_border(contours, info)
                print touched
                with self.rec.a_group():
                    self.rec.record_img('img', img)
                    self.rec.record_plain('info', {
                        'x': x, 'y': y,
                        'area': area,
                        'touched': touched

                    })
                if touched == 'left':
                    self.speed = 0
                    self.direction = -30
                elif touched == 'right':
                    self.speed = 0
                    self.direction = 30
                else:

                    self.speed = 0.2
                    self.direction = (x - HALF_WIDTH) / HALF_WIDTH * 10

    def set_not_found(self):
        self.found = False
        self.direction = 0
        self.speed = 0


if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = ColorTracingTask()
    tttt.walk()
