import tortoise as t

inc = t.p.inclination


class SimpleTask(t.Task):
    def __init__(self):
        super(SimpleTask, self).__init__()

    def step(self):
        print '{}, {}'.format(inc.pitch(), inc.roll())


if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = SimpleTask()
    tttt.walk()
