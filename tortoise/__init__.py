from globals import ctx, peripheral
from recorder import get_recorder
from _tortoise import Tortoise
from task import Task
import config


def update_config(*args, **kwargs):
    if len(*args) == 1:
        for k, v in args[0]:
            kwargs[k] = v

    for k, v in kwargs:
        setattr(config, k, v)


config.update = update_config

p = peripheral
