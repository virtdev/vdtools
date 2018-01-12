# io.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import socket
import struct

def _check(buf):
    if len(buf) < crc.CRC_SIZE:
        return
    tmp = buf[crc.CRC_SIZE:]
    if crc.encode(tmp) == struct.unpack('H', buf[0:crc.CRC_SIZE])[0]:
        return tmp

def send_pkt(sock, buf):
    head = struct.pack('I', len(buf))
    sock.sendall(head)
    if buf:
        sock.sendall(buf)

def recv_bytes(sock, length):
    ret = []
    while length > 0:
        buf = sock.recv(min(length, 2048))
        if not buf:
            raise Exception('Error: failed to receive bytes')
        ret.append(buf)
        length -= len(buf)
    return ''.join(ret)

def recv_pkt(sock):
    head = recv_bytes(sock, 4)
    if not head:
        return ''
    length = struct.unpack('I', head)[0]
    return recv_bytes(sock, length)

def put(sock, buf, local=False):
    buf = str(buf)
    if local:
        send_pkt(sock, buf)
        return
    else:
        raise Exception('Error: I/O error, failed to put')

def get(sock, local=False):
    if local:
        return recv_pkt(sock)
    else:
        raise Exception('Error: I/O error, failed to get')

def connect(addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))
    return sock

def close(sock):
    if sock:
        sock.close()

def listen(addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen(5)
    return sock

def accept(sock):
    return sock.accept()[0]
