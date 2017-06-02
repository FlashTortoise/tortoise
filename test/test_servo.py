from itertools import cycle

import tortoise as t

t.update_config(TORTOISE_WALK_PERIOD=1)


class TestServoTask(t.Task):
    def __init__(self):
        super(TestServoTask, self).__init__()
        self.servo = t.p.servo
        operations = [
            t.p.servo.max, t.p.servo.mid, t.p.servo.min, t.p.servo.mid
        ]

        self.operation_iter = cycle(operations)

    def step(self):
        self.operation_iter.next()()

if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = TestServoTask()
    tttt.walk()
