import time

from tortoise.sensors import Yaw

y = Yaw()

while True:
    print '\r' + str(y.get()),
    time.sleep(0.1)
