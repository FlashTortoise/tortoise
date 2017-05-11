from collections import defaultdict
from contextlib import contextmanager
import copy

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


class GyroScope(object):
    def __init__(self):
        self._s = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=0.05)

    def get(self):
        deg = None
        while deg is None:
            try:
                self._s.write('a')
                self._s.flush()
                st = self._s.read(20)
                deg = float(st)
            except ValueError:
                print 'received %s' % repr(st)

        return deg
