import logging

from globals import ctx, peripheral
from recorder import get_recorder
from _tortoise import Tortoise
from task import Task
import config

overall = logging.getLogger('tortoise')
overall.setLevel(config.LOGGING_LEVEL)
logging.basicConfig()


def update_config(*args, **kwargs):
    if len(args) == 1:
        for k, v in args[0]:
            kwargs[k] = v

    for k, v in kwargs.iteritems():
        setattr(config, k, v)


config.update = update_config

p = peripheral
