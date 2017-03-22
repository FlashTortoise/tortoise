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
        data = json.loads(data)
        w.set_diff(
            data['speed'] * 0.8,
            data['diff'] * 0.18
        )

    receive_callbacks.append(set_wheels)

    server_loop()


if __name__ == '__main__':
    working_loop()
