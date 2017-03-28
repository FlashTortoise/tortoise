import time
from contextlib import contextmanager

from globals import ctx
from sensors import cache_input
from task import Task
from . import config


@contextmanager
def exclusive_run():
    is_task_running = ctx.get('is_task_running', None)
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
        pass
        # Try some other non-interruption solutions
        # raise Exception('running time exceed period')


class Tortoise(object):
    def __init__(self):
        self._task = None
        pass

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, value):
        err_msg = 'Tortoise.task should be assigned by a Task object'
        if isinstance(value, Task):
            self._task = value
        else:
            raise TypeError(err_msg)

    def _validate_task(self):
        if self._task is None:
            raise ValueError('Stepping before specifying task')

    def walk(self):
        self._validate_task()
        try:
            while True:
                with in_a_period():
                    with cache_input():
                        self.task.step()
        except KeyboardInterrupt:
            for fun in ctx.finalization:
                try:
                    fun()
                except Exception as e:
                    print e.message
