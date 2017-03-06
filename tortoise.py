from contextlib import contextmanager
from globals import ctx
from sensors import cache_input


@contextmanager
def exclusive_run():
    is_task_running = getattr(ctx, 'is_task_running', None)
    if is_task_running is True:
        raise Exception('Repeated task start')
    ctx.is_task_running = True
    yield
    ctx.is_task_running = False


class Tortoise(object):
    def __init__(self):
        self.task = None
        pass

    def walk(self):
        with exclusive_run:
            with cache_input:
                self.task.step()
