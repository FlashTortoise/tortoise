from collections import deque


def run_n_time_flag(self, distinct_name, time=1):
    """
    >>> class Something(object):
    ...     def hello(self):
    ...         print '#'*10,
    ...         if run_n_time_flag(self, 'one',time=5):
    ...             print 'executed',
    ...         print 'something'

    >>> s = Something()

    >>> for i in range(20):
    ...     s.hello()

    """
    if getattr(self, '_execute_record', None) is None:
        setattr(self, '_execute_record', {})

    rec = getattr(self, '_execute_record')

    if rec.get(distinct_name, None) is None:
        rec[distinct_name] = time

    if rec[distinct_name] > 0:
        rec[distinct_name] -= 1
        return True
    else:
        return False


class StepManager(object):
    def __init__(self):
        self.tasks = deque()

    def need_step(self):
        task_info = None
        try:
            task_info = self.tasks[0]
        except IndexError:
            return False

        remaining_times = task_info['remaining_times']
        if task_info['remaining_times'] is not None:
            if task_info['remaining_times'] > 0:
                return True
            else:
                raise Exception('Bad condition')

    def add_n_times(self, task, times=1):
        if not callable(task):
            raise Exception('task is not callable')

        self.tasks.append(dict(callable=task, remaining_times=times))

    def step(self):
        self.tasks[0]['remaining_times'] -= 1
        task = self.tasks[0]['callable']
        if self.tasks[0]['remaining_times'] == 0:
            self.tasks.popleft()

        return task()


if __name__ == '__main__':
    class TestStepManager(object):
        def __init__(self):
            self.stepm = StepManager()
            self.executed_count = 0

        def step(self):
            if self.stepm.need_step():
                self.stepm.step()
                return

            print 'raw running'
            if self.executed_count == 5:
                def other_fun():
                    print 'other fun run'
                self.stepm.add_n_times(other_fun)


                def another_fun():
                    print 'another fun run'
                self.stepm.add_n_times(another_fun, 2)

            self.executed_count += 1

    t = TestStepManager()
    for i in range(10):
        t.step()


