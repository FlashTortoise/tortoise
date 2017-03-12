import time
from contextlib import contextmanager

from globals import ctx
from sensors import cache_input
from . import config

PERIOD = 0.1


@contextmanager
def exclusive_run():
    is_task_running = getattr(ctx, 'is_task_running', None)
    if is_task_running is True:
        raise Exception('Repeated task start')
    ctx.is_task_running = True
    yield
    ctx.is_task_running = False


@contextmanager
def in_a_period():
    s_time = time.time()
    yield
    remaining = config.TORTOISE_WALK_PERIOD - (time.time() - s_time)
    if remaining > 0:
        time.sleep(remaining)
    else:
        raise Exception('running time exceed period')


class Tortoise(object):
    def __init__(self):
        self.task = None
        pass

    def walk(self):
        while True:
            with in_a_period:
                with cache_input:
                    self.task.step()
