from . import config


class Wheels(object):
    def __init__(self):
        # noinspection PyUnresolvedReferences
        from gpiozero import Motor
        self.Motor = Motor
        self.mq = Motor(*config.WHEELS_PINS_LF)
        self.ma = Motor(*config.WHEELS_PINS_LB)
        self.mw = Motor(*config.WHEELS_PINS_RF)
        self.ms = Motor(*config.WHEELS_PINS_RB)

    def set(self, l, r):
        self.set_lr(l, r)

    def set_lr(self, l, r):
        self.set_raw(l, l, r, r)

    def set_diff(self, speed, diff):
        self.set_lr(speed-diff, speed+diff)

    def set_raw(self, q, a, w, s):
        self.mq.value = q
        self.ma.value = a
        self.mw.value = w
        self.ms.value = s
