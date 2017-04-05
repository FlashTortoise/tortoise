import json

import sys

sys.path.append('../')

from tcp_server import (
    receive_callbacks,
    working_loop as server_loop)
from tortoise.globals import peripheral


def working_loop():
    w = peripheral.wheels

    def constrain(a, l, u):
        if a > u:
            return u
        elif a < l:
            return l
        else:
            return a

    def set_wheels(data):
        try:
            data = json.loads(data)
            print data
            w.set_lr(
                constrain((data['x'] ** 2 + data['y'] ** 2) ** 0.5 + data['x'],
                          -1, 1),
                constrain((data['x'] ** 2 + data['y'] ** 2) ** 0.5 - data['x'],
                          -1, 1),
            )
        except ValueError:
            pass

    receive_callbacks.append(set_wheels)

    server_loop()


if __name__ == '__main__':
    working_loop()
