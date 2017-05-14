import time

from tortoise.sensors import GyroScope

g = GyroScope()

while True:
    print '\r' + str(g.get()),
    time.sleep(0.1)
