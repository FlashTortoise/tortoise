from tortoise import config

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


class Peripheral(object):
    @property
    def eye(self):
        # type: () -> Eye
        if getattr(self, '_eye', None) is None:
            if config.EYE_SIMULATOR_ACTIVE:
                from tortoise.sensors import EyeSimulator as Eye
            else:
                from tortoise.sensors import Eye
            setattr(self, '_eye', Eye())
        return getattr(self, '_eye')

    @property
    def wheels(self):
        # type: () -> Wheels
        if getattr(self, '_wheels', None) is None:
            from tortoise.effectors import Wheels
            setattr(self, '_wheels', Wheels())
        return getattr(self, '_wheels')


ctx = ContextGlobal()
ctx.finalization = []

peripheral = Peripheral()
