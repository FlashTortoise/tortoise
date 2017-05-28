import time

import tortoise as t
from tortoise.effectors import RxTx

t.update_config(CONTROLLER_PORT_REGEX='usbmodem')

rt = RxTx()

rt.send('hello')

time.sleep(0.1)

print rt.recv()
