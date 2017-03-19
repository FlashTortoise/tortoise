from . import config

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


class Peripheral(ContextGlobal):
    def __getattr__(self, item):
        if item in config.PERIPHERAL_SUPPORTED.keys():
            import_string = config.PERIPHERAL_SUPPORTED[item]
            module, cls = import_string.rsplit('.', 1)

            module = __import__(module, fromlist=[cls])
            cls = getattr(module, cls)

            self.__dict__['item'] = cls()
        else:
            raise AttributeError("Tortoise doesn't have such peripheral")


ctx = ContextGlobal()
ctx.finalization = []

peripheral = Peripheral()
