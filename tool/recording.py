from sys import argv, exit

from tortoise import get_recorder, peripheral, Tortoise, Task


class RecordingTask(Task):
    def __init__(self, name):
        super(RecordingTask, self).__init__()
        self.rec = get_recorder(name)
        self.eye = peripheral.eye
        self.wheels = peripheral.wheels

    def step(self):
        with self.rec.a_group():
            self.rec.record_plain('speeds', self.wheels.get_raw())

            self.rec.record_img('img', self.eye.see())


def record_working_loop(name='default_rec'):
    t = Tortoise()
    t.task = RecordingTask(name)
    t.walk()


if __name__ == '__main__':
    hint = '''Usage:\n
        -n<record file name> : specify record file name
        -h<help> : show help message
    '''

    if len(argv) > 2:
        print 'Error: too many arguments'
        print hint
        exit(-1)

    if len(argv) == 2:
        arg = argv[1]
        key, value = [None] * 2
        if len(arg) >= 2:
            if arg[0:2] not in {'-n', '-h'}:
                print 'Error: unsupported argument'
                print hint
                exit(-1)
            else:
                key, value = arg[0:2], arg[2:]

        if key == '-h':
            print hint
        elif key == '-n':
            record_working_loop(name=value)

    elif len(argv) == 1:
        record_working_loop()
