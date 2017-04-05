# coding=utf-8
import socket
import pygame
import pygame.joystick as joystick
import time
import json

JOYSTICK_ID = 0
PERIOD = 0.1
ADDRESS = '192.168.1.1'
PORT = 9999


def constrain(a, l, u):
    if a > u:
        return u
    elif a < l:
        return l
    else:
        return a


def prepare_control_signal(j):
    # type: (joystick.JoystickType) -> dict
    y = -j.get_axis(1)
    x = j.get_axis(2)

    l = constrain((x ** 2 + y ** 2) ** 0.5 + x, -1, 1)
    r = constrain((x ** 2 + y ** 2) ** 0.5 - x, -1, 1)
    return {'l': l, 'r': r}


PREPARE_SIGNAL_FROM_JOYSTICK = prepare_control_signal

# Initialize joystick
pygame.init()
ctr = joystick.Joystick(JOYSTICK_ID)
ctr.init()

# Establish a connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ADDRESS, PORT))

# Use try-finally block to properly close sockets
try:
    while True:
        # For pygame work normally
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass

        s.send(json.dumps(
            PREPARE_SIGNAL_FROM_JOYSTICK(ctr)
        ))

        value = ctr.get_axis(1)
        print '\r', ctr.get_axis(1),

        time.sleep(PERIOD)
finally:
    s.send('exit')
    s.close()
