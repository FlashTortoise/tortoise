import random
import string

from tortoise.recorder import get_recorder
from tortoise._tortoise import Tortoise
from tortoise.globals import peripheral


class RecordingTask:
    def __init__(self):
        self.rec = get_recorder('test_rec')
        self.eye = peripheral.eye
        self.wheels = peripheral.wheels

    def step(self):
        with self.rec.a_group():
            self.rec.record_plain('speeds', self.wheels.get_raw())

            self.rec.record_img('img', self.eye.see())


def record_working_loop():
    t = Tortoise()
    t.task = RecordingTask()
    t.walk()


if __name__ == '__main__':
    record_working_loop()
