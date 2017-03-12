_sentinel = object()


class ContextGlobal(object):
    def __init__(self):
        pass

    def get(self, name, default=None):
        return self.__dict__.get(name, default)

    def pop(self, name, default=_sentinel):
        if default is _sentinel:
            return self.__dict__.pop(name)
        else:
            return self.__dict__.pop(name, default)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return self.__dict__.__iter__()

ctx = ContextGlobal()
