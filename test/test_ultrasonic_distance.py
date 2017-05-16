import time

from tortoise.sensors import Ranging as Dis

d = Dis()

while True:
    st = time.time()
    for i in range(5):
        print "%9.0f" % d.get(i),

    ed = time.time()
    print '   ', st - ed

    print

    time.sleep(1)
