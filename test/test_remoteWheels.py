import time

from tortoise.effectors import RemoteWheels

w = RemoteWheels()

for i in range(4):
    speeds = [0] * 4

    print "wheel {} is setting to 1".format(i)
    speeds[i] = 0.2
    w.set_raw(*speeds)
    # time.sleep(1)
    raw_input('pause')

    print "wheel {} is setting to -1".format(i)
    speeds[i] = -0.2
    w.set_raw(*speeds)
    # time.sleep(1)
    raw_input('pause')

w.set_raw(*([0] * 4))
