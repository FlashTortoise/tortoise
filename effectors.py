
class Wheels(object):
    def __init__(self):
        # noinspection PyUnresolvedReferences
        from gpiozero import Motor
        self.Motor = Motor
        self.mq, self.mw, self.ma, self.ms = map(
            Motor, []*4
        )

    def set(self, l, r):
        self.set_lr(l, r)

    def set_lr(self, l, r):
        self.set_raw(l, l, r, r)

    def set_diff(self, speed, diff):
        self.set_lr(speed-diff, speed+diff)

    def set_raw(self, q, a, w, s):
        map(self.Motor.value,
            (self.mq, self.ma, self.mw, self.ms),
            (q, a, w, s))
