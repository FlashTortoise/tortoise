from multiprocessing import Lock

import logging
import serial

from tortoise import helper
from tortoise.globals import ctx
from . import config


class ExternalController(object):
    logger = logging.getLogger('tortoise.p.mcu')

    def __init__(self):
        self._s = s = serial.Serial()
        s.baudrate = config.CONTROLLER_BAUDRATE
        s.port = self._get_port()
        # todo: let non-blocking safe
        # s.timeout = 1
        s.open()

        ctx.finalization.append(lambda: s.close())

    @classmethod
    def _get_port(cls):
        import serial.tools.list_ports as lp

        devs = [p for p in lp.grep(config.CONTROLLER_PORT_REGEX)]
        sport = None

        if len(devs) == 0:
            cls.logger.error('None of serial port satisfy condition')
            raise Exception('None of serial port satisfy condition')
        elif len(devs) == 1:
            sport = devs[0]
        else:
            raise Exception('Multiple device satisfies regex')

        cls.logger.info('Chosen: {}'.format(sport.device))

        return sport.device

    def command(self, cmd):
        # type: (str) -> (str, None)
        # Pack command
        t_pack = '${}#{:0=2x}'.format(
            cmd, sum([ord(c) for c in '$' + cmd]) & 0xff)
        # Send command
        self._s.write(t_pack)
        self._s.flush()

        # Gather reply
        r_pack = self._s.read_until('#') + self._s.read(2)
        # Check if has checksum
        if r_pack[-3] != '#':
            return None
        # Check pack head index
        start = r_pack.rfind('+$')
        if start == -1:
            # No head
            return None
        elif start != 0:
            # Aborted data exist
            # Some warning
            pass

        # Calculate checksum
        reply_sum = sum(map(ord, r_pack[start:-3])) & 0xff
        trans_sum = int(r_pack[-2:], base=16)
        reply = r_pack[start + 2:-3]
        return reply if reply_sum == trans_sum else None


class Wheels(object):
    def __init__(self):
        # noinspection PyUnresolvedReferences
        from gpiozero import Motor
        self.Motor = Motor
        self.mq = Motor(*config.WHEELS_PINS_LF)
        self.ma = Motor(*config.WHEELS_PINS_LB)
        self.mw = Motor(*config.WHEELS_PINS_RF)
        self.ms = Motor(*config.WHEELS_PINS_RB)

        self._cache_speed = [
            0, 0, 0, 0
        ]
        self._read_lock = Lock()

    def set_lr(self, l, r):
        self.set_raw(l, l, r, r)

    def set_diff(self, speed, diff):
        self.set_lr(speed-diff, speed+diff)

    def set_raw(self, q, a, w, s):
        self.mq.value = q
        self.ma.value = a
        self.mw.value = w
        self.ms.value = s

        with self._read_lock:
            self._cache_speed = q, w, a, s

    def get_raw(self):
        with self._read_lock:
            return tuple(self._cache_speed)

    def get_lr(self):
        q, w, a, s = self.get_raw()
        return (q + w) / 2, (w + s) / 2

    def get_diff(self):
        l, r = self.get_lr()
        return (l + r) / 2, (r - l) / 2

    raw = property(get_raw)
    lr = property(get_lr)
    diff = property(get_diff)

    @raw.setter
    def raw(self, value):
        self.set_raw(*value)

    @lr.setter
    def lr(self, value):
        self.set_lr(*value)

    @diff.setter
    def diff(self, value):
        self.set_diff(*value)


# noinspection PyMissingConstructor
class WheelsSimulator(Wheels):
    def __init__(self):
        # noinspection PyUnresolvedReferences
        class Motor(object):
            def __init__(self, *args):
                self.value = 0

        self.Motor = Motor
        self.mq = Motor(*config.WHEELS_PINS_LF)
        self.ma = Motor(*config.WHEELS_PINS_LB)
        self.mw = Motor(*config.WHEELS_PINS_RF)
        self.ms = Motor(*config.WHEELS_PINS_RB)

        self._cache_speed = [
            0, 0, 0, 0
        ]
        self._read_lock = Lock()


class RemoteWheels(object):
    logger = logging.getLogger('tortoise.p.wheels')

    def __init__(self):
        from tortoise.globals import peripheral as p
        self.mcu = p.mcu

        self._cache_speed = [
            0, 0, 0, 0
        ]
        self._read_lock = Lock()

    def set_lr(self, l, r):
        """
        Set wheels speed by specifying left and right speeds
        :param l: Left wheel speeds
        :param r: Right wheel speeds
        """
        self.set_raw(l, l, r, r)

    def set_diff(self, speed, diff):
        self.set_lr(speed - diff, speed + diff)

    def set_raw(self, q, a, w, s):
        cmd_word = 'm{:.2f} {:.2f} {:.2f} {:.2f}'.format(
            *[helper.mlimit(v, 1) for v in [q, a, w, s]])

        self.logger.debug('sent command word: "{}"'.format(cmd_word))

        rtn = self.mcu.command(cmd_word)
        if rtn != 'OK':
            self.logger.warn('set wheels failed')

        with self._read_lock:
            self._cache_speed = q, w, a, s

    def get_raw(self):
        with self._read_lock:
            return tuple(self._cache_speed)

    def get_lr(self):
        q, w, a, s = self.get_raw()
        return (q + w) / 2, (w + s) / 2

    def get_diff(self):
        l, r = self.get_lr()
        return (l + r) / 2, (r - l) / 2

    raw = property(get_raw)
    lr = property(get_lr)
    diff = property(get_diff)

    @raw.setter
    def raw(self, value):
        self.set_raw(*value)

    @lr.setter
    def lr(self, value):
        self.set_lr(*value)

    @diff.setter
    def diff(self, value):
        self.set_diff(*value)


class RxTx(object):
    logger = logging.getLogger('tortoise.p.rxtx')

    def __init__(self):
        self.logger.info('Init')
        from tortoise.globals import peripheral as p
        self.mcu = p.mcu

    def send(self, message):
        # type: (str) -> None
        def trim_length(s, length):
            while len(s) >= length:
                st, s = s[0:length], s[length:]
                yield st
            yield s

        for msglet in trim_length(message, 80):
            self.mcu.command('w' + msglet)

    def recv(self):
        reply = ''
        while True:
            part = self.mcu.command('r')
            if part == '!NO_DATA':
                break
            else:
                reply += part

        return reply
