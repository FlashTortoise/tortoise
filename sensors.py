from collections import defaultdict
from contextlib import contextmanager

from globals import ctx

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


class Recorder(object):
    def __init__(self):
        pass

    def record_img(self, var):
        pass

    def record_plain(self, var):
        pass

    @contextmanager
    def a_group(self):
        pass


class Eye(object):
    def __init__(self):
        pass

    @with_cache
    def see(self):
        pass
