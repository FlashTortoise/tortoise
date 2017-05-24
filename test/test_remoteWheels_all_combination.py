import time

import itertools

from tortoise.effectors import RemoteWheels

w = RemoteWheels()


def all_combinations(num=4):
    for i in range(num):
        print 'select %d: ' % (i + 1)
        for j in itertools.combinations(range(4), i + 1):
            speeds = [0] * 4
            for ii in j:
                speeds[ii] = 1
            yield speeds


try:
    for speeds in all_combinations():
        print speeds

        vs = [v * 0.2 for v in speeds]
        print vs
        w.set_raw(*vs)
        # time.sleep(1)
        raw_input('pause')

        # vs = [v * -0.2 for v in speeds]
        # print vs
        # w.set_raw( *vs )
        # # time.sleep(1)
        # raw_input('pause')
finally:
    w.set_raw(*([0] * 4))
