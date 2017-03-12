from collections import defaultdict
from contextlib import contextmanager

from globals import ctx
from . import config

ctx.sensing_cache = defaultdict(lambda: None)


def with_cache(f):
    def fun(self, cached=True, *args, **kwargs):
        if cached is True:
            cache = ctx.sensing_cache
            if cache[self] is None:
                cache[self] = f(self, *args, **kwargs)
            return cache[self]
        else:
            return f(self, *args, **kwargs)

    return fun


@contextmanager
def cache_input():
    ctx.sensing_cache.clear()
    yield


class Eye(object):
    def __init__(self):
        import cv2
        self._cap = cv2.VideoCapture(config.EYE_CAPTURE_ID)

        width, height = config.EYE_SIGHT_HEIGHT, config.EYE_SIGHT_WIDTH
        if height is not None and width is not None:
            self._cap.set(3, width)
            self._cap.set(4, width)

    @with_cache
    def see(self):
        _, img = self._cap.read()
        while img is None:
            img = self._cap.get()
        return img
