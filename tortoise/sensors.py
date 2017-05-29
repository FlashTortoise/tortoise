from collections import defaultdict
from contextlib import contextmanager
import copy
import math

import cv2
import numpy
import serial

from globals import ctx
from . import config

ctx.sensing_cache = defaultdict(lambda: None)


def with_cache(f):
    def fun(self, cached=True, *args, **kwargs):
        if cached is True:
            cache = ctx.sensing_cache
            if cache[self] is None:
                cache[self] = f(self, *args, **kwargs)
            return copy.copy(cache[self])
        else:
            return f(self, *args, **kwargs)

    return fun


@contextmanager
def cache_input():
    """
    Decorator that used to keep the sensed data unchanged. Or, in other word,
    specifying the block of code that using only one captured value.
    """
    ctx.sensing_cache.clear()
    yield


class Eye(object):
    def __init__(self):
        self._cap = cv2.VideoCapture(config.EYE_CAPTURE_ID)

        width, height = config.EYE_SIGHT_HEIGHT, config.EYE_SIGHT_WIDTH
        if height is None or width is None:
            raise ValueError('configuration of eye sight cannot be None')

        ctx.finalization.append(lambda: self._cap.release())

    @with_cache
    def see(self):
        # type: () -> numpy.ndarray
        """
        :return: What viewed as numpy ndarray
        """
        _, img = self._cap.read()
        while img is None:
            img = self._cap.get()
        return cv2.resize(img, dsize=(
            config.EYE_SIGHT_WIDTH, config.EYE_SIGHT_HEIGHT))


# noinspection PyMissingConstructor
class EyeSimulator(Eye):
    def __init__(self):
        self.data = config.EYE_SIMULATOR_DATASET

        height, width = config.EYE_SIGHT_HEIGHT, config.EYE_SIGHT_WIDTH
        if height is not None and width is not None:
            self._width, self._height = width, height
        else:
            self._width = self._height = None

    @with_cache
    def see(self):
        # type: () -> numpy.ndarray
        """
        :return: What faked as numpy ndarray
        """
        img = self.data.next()
        if self._width is not None:
            img = cv2.resize(img, dsize=(self._width, self._height))
        return img


class Yaw(object):
    def __init__(self):
        from tortoise import p
        self.mcu = p.mcu

    def get(self):
        return float(self.mcu.command('g'))


class Inclination(object):
    def __init__(self):
        from tortoise import p
        self.mcu = p.mcu
        self.h = self.r = self.d = 0

    def _gather(self):
        a = 1
        while True:
            a = self.mcu.command('a').split(',')
            if len(a) == 3:
                try:
                    self.h, self.r, self.d = [float(f) for f in a]
                except ValueError:
                    pass
                else:
                    break

        self.abs = math.sqrt(self.h ** 2 + self.r ** 2 + self.d ** 2)

    def pitch(self):
        rad = math.asin(self.h / math.sqrt(self.h ** 2 + self.d ** 2))
        if self.d > 0:
            rad = -rad
        return math.degrees(rad)

    def roll(self):
        rad = math.asin(self.r / math.sqrt(self.r ** 2 + self.d ** 2))
        if self.d > 0:
            rad = -rad
        return math.degrees(rad)



class Ranging(object):
    def __init__(self):
        from tortoise import p
        self.mcu = p.mcu

    def get(self, i):
        assert 0 <= i <= 5
        d = self.mcu.command('u%d' % i)
        if d == '!DISTANCE':
            return .0
        else:
            return float(d)
