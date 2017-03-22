from multiprocessing import Lock

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

        self._cache_speed = [
            0, 0,
            0, 0
        ]
        self._read_lock = Lock()

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

        with self._read_lock:
            self._cache_speed = q, w, a, s

    def get_raw(self):
        with self._read_lock:
            return tuple(self._cache_speed)

    def get_lr(self):
        q, w, a, s = self.get_raw()
        return (q + w) / 2, (w + s) / 2

    def get_diff(self):
        l, r = self.get_lr()
        return (l + r) / 2, (r - l) / 2
