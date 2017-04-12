import json
from tcp_server import (
    receive_callbacks,
    working_loop as server_loop)
from tortoise.globals import peripheral


def working_loop():
    w = peripheral.wheels

    def set_wheels(data):
        try:
            data = json.loads(data)
            print data
            w.set_lr(**data)
        except ValueError:
            pass

    receive_callbacks.append(set_wheels)

    server_loop()


if __name__ == '__main__':
    working_loop()
