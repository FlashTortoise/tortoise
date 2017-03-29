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

SENDING_FIELDS = {
    'y': lambda j: -joystick.JoystickType.get_axis(j, 1),
    'x': lambda j: joystick.JoystickType.get_axis(j, 2)
}

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

        s.send(json.dumps({
                              k: v(ctr) for k, v in SENDING_FIELDS.iteritems()
                              }))

        value = ctr.get_axis(1)
        print '\r', ctr.get_axis(1),

        time.sleep(PERIOD)
finally:
    s.send('exit')
    s.close()
