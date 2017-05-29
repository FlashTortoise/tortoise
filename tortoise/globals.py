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
    def mcu(self):
        # type: () -> ExternalController
        if getattr(self, '_mcu', None) is None:
            from tortoise.effectors import ExternalController
            setattr(self, '_mcu', ExternalController())
        return getattr(self, '_mcu')

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
            if config.PERIPHERAL_USE_REMOTE_WHEELS:
                from tortoise.effectors import RemoteWheels as Wheels
            else:
                from tortoise.effectors import Wheels
            setattr(self, '_wheels', Wheels())
        return getattr(self, '_wheels')

    @property
    def yaw(self):
        # type: () -> Yaw
        if getattr(self, '_yaw', None) is None:
            from tortoise.sensors import Yaw
            setattr(self, '_yaw', Yaw())
        return getattr(self, '_yaw')

    @property
    def ranging(self):
        # type: () -> Ranging
        if getattr(self, '_ranging', None) is None:
            from tortoise.sensors import Ranging
            setattr(self, '_ranging', Ranging())
        return getattr(self, '_ranging')

    @property
    def rxtx(self):
        # type: () -> RxTx
        if getattr(self, '_rxtx', None) is None:
            from tortoise.effectors import RxTx
            setattr(self, '_rxtx', RxTx())
        return getattr(self, '_rxtx')

    @property
    def inclination(self):
        # type () -> Inclination
        if getattr(self, '_inclination', None) is None:
            from tortoise.sensors import Inclination
            setattr(self, '_inclination', Inclination())
        return getattr(self, '_inclination')


ctx = ContextGlobal()
ctx.finalization = []

peripheral = Peripheral()
