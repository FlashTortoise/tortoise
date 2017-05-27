import tortoise as t


class SimpleTask(t.Task):
    def __init__(self):
        super(SimpleTask, self).__init__()

    def step(self):
        print 'hello'


if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = SimpleTask()
    tttt.walk()
