from collections import deque
from itertools import repeat
from more_itertools import peekable


"""Constrain helper function"""


def limit(a, l, u):
    if a > u:
        return u
    elif a < l:
        return l
    else:
        return a


def closure_limit(l, u):
    def limit(a):
        if a > u:
            return u
        elif a < l:
            return l
        else:
            return a

    return limit


def mlimit(a, m):
    if a > m:
        return m
    elif a < -m:
        return -m
    else:
        return a


def closure_mlimit(m):
    def limit(a):
        if a > m:
            return m
        elif a < -m:
            return -m
        else:
            return a

    return limit


""" Non-blocking helpers """


def run_n_time_flag(self, distinct_name, time=1, peek=False):
    if getattr(self, '_execute_record', None) is None:
        setattr(self, '_execute_record', {})

    rec = getattr(self, '_execute_record')

    if rec.get(distinct_name, None) is None:
        rec[distinct_name] = time

    if rec[distinct_name] > 0:
        if peek is False:
            rec[distinct_name] -= 1
        return True
    else:
        return False


class StepManager(object):
    def __init__(self):
        self.tasks = deque()

    def need_step(self):
        while True:
            try:
                task_info = self.tasks[0]
            except IndexError:
                return False

            try:
                p = task_info['need_iter'].peek()
            except StopIteration:
                p = False

            if p is False:
                self.tasks.popleft()
            else:
                return True

    def add_n_times(self, step, times):
        if not callable(step):
            raise Exception('task is not callable')

        self.tasks.append(dict(
            callable=step,
            need_iter=peekable(repeat(True, times))
        ))

    def add(self, step):
        self.add_n_times(step, times=1)

    def add_blocking(self, step, until):
        self.tasks.append(dict(
            callable=step,
            need_iter=peekable(iter(until, None))
        ))

    def step(self):
        need_iter = self.tasks[0]['need_iter'].next()
        task = self.tasks[0]['callable']
        if not need_iter:
            self.tasks.popleft()

        return task()
