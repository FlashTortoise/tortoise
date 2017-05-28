import argparse
import readline
import code
from functools import wraps

import serial
import re

import sys


def get_port(port_regex):
    import serial.tools.list_ports as lp

    devs = [p for p in lp.grep(port_regex)]
    sport = None

    if len(devs) == 0:
        raise Exception('None of serial port satisfy condition')
    elif len(devs) == 1:
        sport = devs[0]
    else:
        for i, p in enumerate(lp.comports()):
            print '[{}]\t{}'.format(i, p)

        idx = raw_input('Choose one by index: ')
        sport = devs[int(idx)]

    print 'Chosen: ', sport.device

    return sport.device


s = None


def command(word):
    s.write(word)
    return s.readline().strip('\r\n')


def get_configs():
    baud = re.match(
        r'OK\+B(\d+)',
        command('AT+RB')).group(1)
    channel = re.match(
        r'OK\+RC(\d+)',
        command('AT+RC')).group(1)
    fu = re.match(
        r'OK\+FU(\d+)',
        command('AT+RF')).group(1)
    power = re.match(
        'OK\\+RP:(.+)',
        command('AT+RP')).group(1)

    # print [c for c in (baud, channel, fu, repr(power))]
    return dict(baud=int(baud), channel=int(channel), fu=int(fu), power=power)


def configure(baud=None, channel=None, fu=None, power=None):
    cmds = []

    if baud is not None:
        cmds.append('AT+B%d' % baud)
    if channel is not None:
        cmds.append('AT+C{:0>3d}'.format(channel))
    if fu is not None:
        cmds.append('AT+FU%d' % fu)
    if power is not None:
        cmds.append('AT+P%d' % power)

    for cmd in cmds:
        print 'command: ', repr(cmd)
        if not command(cmd).startswith('OK+'):
            print '\t\t\033[0;31mERROR'
        else:
            print '\t\t\033[0;32mOK',
        print


def _config(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        cmd = fun(*args, **kwargs)

        ack = command(cmd)
        if ack.startswith('OK'):
            print '\033[0;32m{}\x1b[0m'.format(ack)
        else:
            print '\033[0;31m{}\x1b[0m'.format(ack)

    return wrapper


@_config
def default():
    """
    default()
    Set model to default
    """
    return 'AT+DEFAULT'


@_config
def baud(value=None):
    """
    baud(value=None)
    Manipulate baud rate of wireless model, configure or query.

    value: Desired baud rate, keep blank for query. (Alternatives: 1200bps,
        2400bps, 4800bps, 9600bps, 19200bps, 38400bps, 57600bps, 115200bps)
    """
    if value is None:
        return 'AT+RB'
    else:
        return 'AT+B%d' % value


@_config
def channel(value=None):
    """
    channel(value=None)
    Manipulate channel of wireless model, configure or query.

    value: Desired channel, keep blank for query. It should in range from 1
        to 127, with a step of 5.
    """
    if value is None:
        return 'AT+RC'
    else:
        return 'AT+C{:0>3d}'.format(value)


@_config
def fu(value=None):
    """
    fu(value=None)
    Manipulate transmission mode of wireless model, configure or query.

    value: Desired channel, keep blank for query.
        1 - Semi-power saving mode
        2 - Power saving mode
        3 - Normal mode
        4 - Long distance mode
    """
    if value is None:
        return 'AT+RF'
    else:
        return 'AT+FU%d' % value


@_config
def power(value=None):
    """
    power(value=None)
    Manipulate transmission power of wireless model, configure or query.

    value: Desired power for transmission, keep blank for query.
        1 - -1 dBm         5 - 11 dBm
        2 -  2 dbm         6 - 14 dBm
        3 -  5 dBm         7 - 17 dBm
        4 -  8 dBm         8 - 20 dBm
    """
    if value is None:
        return 'AT+RP'
    else:
        return 'AT+P%d' % value


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port',
        help='name or part of name of port.',
        default=''
    )
    parser.add_argument(
        '--baud',
        help='specifying baud rate. (default is 9600)',
        type=int,
        default=9600
    )

    args = parser.parse_args()

    port = get_port(args.port)
    s = serial.Serial(port=port, baudrate=args.baud)

    if command('AT') != 'OK':
        print >> sys.stderr, 'Configure connection test failed. ' \
                             'Check connection and mode.'
        sys.exit(0)

    for k, v in get_configs().iteritems():
        print '\033[0;34m{: <9s}: \033[0m{}'.format(k, v)

    print
    print 'commands: default, baud, channel, fu, power'
    print 'help(...) for usage'

    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()
