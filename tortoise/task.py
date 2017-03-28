from abc import abstractmethod


class Task(object):
    def __init__(self):
        pass

    @abstractmethod
    def step(self):
        """
        Run every certain period. Abstract method.
        Do not include any forever loop in this function.
        :rtype: None
        """
        pass

    def finalize(self):
        """
        Run when destroy the task object. Intend to release resources and so on.
        Override is not forced.

        """
        pass
