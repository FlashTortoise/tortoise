import pkgutil
import time
from contextlib import contextmanager
import sys, os

from globals import ctx
from sensors import cache_input
from config import Config

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
    remaining = PERIOD - (time.time() - s_time)
    if remaining > 0:
        time.sleep(remaining)
    else:
        raise Exception('running time exceed period')


def get_root_path(import_name):
    """Returns the path to a package or cwd if that cannot be found.  This
    returns the path of a package or the folder that contains a module.

    Not to be confused with the package path returned by :func:`find_package`.
    """
    # Module already imported and has a file attribute.  Use that first.
    mod = sys.modules.get(import_name)
    if mod is not None and hasattr(mod, '__file__'):
        return os.path.dirname(os.path.abspath(mod.__file__))

    # Next attempt: check the loader.
    loader = pkgutil.get_loader(import_name)

    # Loader does not exist or we're referring to an unloaded main module
    # or a main module without path (interactive sessions), go with the
    # current working directory.
    if loader is None or import_name == '__main__':
        return os.getcwd()


class Tortoise(object):
    def __init__(self, import_name):
        self.task = None
        root_path = get_root_path(import_name)
        ctx.config = Config(root_path)
        pass

    def walk(self):
        while True:
            with in_a_period:
                with cache_input:
                    self.task.step()
