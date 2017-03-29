# coding=utf-8
import socket
import threading

receive_callbacks = []


def print_json(data):
    print '\r', data,


receive_callbacks.append(print_json)


def tcp_link(sock, addr):
    print 'Accept new connection from %s:%s...' % addr

    # Receive message from a socket
    while True:
        data = sock.recv(1024)
        if data == 'exit' or not data:
            break

        # Notify all callbacks
        for cb in receive_callbacks:
            cb(data)

    sock.close()
    print 'Connection from %s:%s closed.' % addr


def working_loop():
    # Create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('192.168.1.1', 9999))
    s.listen(1)

    # Service Loop
    while True:
        # Accept a new connection
        sock, addr = s.accept()

        # Use a new daemon thread to handle the connection
        t = threading.Thread(target=tcp_link, args=(sock, addr))
        t.setDaemon(True)
        t.start()


if __name__ == '__main__':
    working_loop()
