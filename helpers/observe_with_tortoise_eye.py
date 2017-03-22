import socket
import threading
import time

from contextlib import contextmanager

import cv2
import numpy as np

import sys

sys.path.append('../')

PERIOD = 0.1

ADDRESS = '192.168.1.1'
PORT = 10000


@contextmanager
def in_a_period():
    s_time = time.time()
    yield
    remaining = PERIOD - (time.time() - s_time)
    if remaining > 0:
        time.sleep(remaining)
    else:
        # raise Exception('running time exceed period')
        pass


eye = None


def tcp_link(sock, addr):
    print 'Accept new connection from %s:%s...' % addr

    try:
        # Receive message from a socket
        while True:
            with in_a_period():
                img = eye.see(cached=False)
                rtn, jpg = cv2.imencode('.jpg', img)
                jpg = jpg.tostring()

                # Send frame head: fix sized byte count
                sock.send(str(len(jpg)).ljust(16))
                # Send data
                sock.send(jpg)
    except Exception as e:
        print e
    finally:
        sock.close()
    print 'Connection from %s:%s closed.' % addr


def tortoise_working_loop():
    # Initialize Eye
    from tortoise.globals import peripheral
    global eye
    eye = peripheral.eye

    # Create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ADDRESS, PORT))
    s.listen(1)

    # Service Loop
    while True:
        # Accept a new connection
        sock, addr = s.accept()

        # Use a new daemon thread to handle the connection
        t = threading.Thread(target=tcp_link, args=(sock, addr))
        t.setDaemon(True)
        t.start()


def _recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def monitor_working_loop():
    # Establish a connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ADDRESS, PORT))

    # Use try-finally block to properly close sockets
    try:
        while True:
            l = _recvall(s, 16)

            if not l:
                print 'no data'
                time.sleep(0.1)
                continue

            print l
            jpg = _recvall(s, int(l))
            img = cv2.imdecode(np.fromstring(jpg, np.uint8), 1)
            cv2.imshow('test', img)
            if cv2.waitKey(20) & 0xFF == 27:
                break
    finally:
        cv2.destroyAllWindows()
        s.send('exit')
        s.close()


if __name__ == '__main__':
    import os

    if os.name == 'posix' and \
                    os.environ['USER'] == 'pi':
        tortoise_working_loop()


    else:
        import sys

        if len(sys.argv) > 1 and sys.argv[1] == 'm':
            monitor_working_loop()
        else:
            i = raw_input('Monitor or Eyeing ([m]/e)')
            if i == '' or i == 'm':
                monitor_working_loop()
            else:
                tortoise_working_loop()
