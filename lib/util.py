#      util.py
#      
#      Copyright (C) 2014 Yi-Wei Ci <ciyiwei@hotmail.com>
#      
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#      
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#      
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#      MA 02110-1301, USA.

import os
import imp
import struct

UID_SIZE = 32
DEFAULT_UID = '0' * UID_SIZE
DEVNULL = open(os.devnull, 'wb')

DIR_MODE = 0o755
FILE_MODE = 0o644

_default_addr = None

def zmqaddr(addr, port):
    return 'tcp://%s:%d' % (str(addr), int(port))

def hash_name(name):
    length = len(name)
    if length > 1:
        return (ord(name[-2]) << 8) + ord(name[-1])
    elif length == 1:
        return ord(name[-1])
    else:
        return 0

def service_start(*args):
    for srv in args:
        srv.start()

def service_join(*args):
    for srv in args:
        srv.join()

def send_pkt(sock, buf):
    head = struct.pack('I', len(buf))
    sock.sendall(head)
    if buf:
        sock.sendall(buf)

def _recv(sock, length):
    ret = []
    while length > 0:
        buf = sock.recv(min(length, 2048))
        if not buf:
            raise Exception('failed to receive')
        ret.append(buf)
        length -= len(buf) 
    return ''.join(ret)

def recv_pkt(sock):
    head = _recv(sock, 4)
    if not head:
        return ''
    length = struct.unpack('I', head)[0]
    return _recv(sock, length)

def close_port(port):
    cmd = 'lsof -i:%d -Fp | cut -c2- | xargs --no-run-if-empty kill -9' % port
    os.system(cmd)

def lock(func):
    def _lock(*args, **kwargs):
        self = args[0]
        self._lock.acquire()
        try:
            return func(*args, **kwargs)
        finally:
            self._lock.release()
    return _lock

def named_lock(func):
    def _named_lock(*args, **kwargs):
        self = args[0]
        name = args[1]
        self._lock.acquire(name)
        try:
            return func(*args, **kwargs)
        finally:
            self._lock.release(name)
    return _named_lock

def mount_device(uid, name, mode, freq, prof):
    pass

DRIVER_PATH = os.path.join(os.getcwd(), 'drivers')

def load_driver(typ, name=None, sock=None):
    try:
        module = imp.load_source(typ, os.path.join(DRIVER_PATH, '%s.py' % typ.lower()))
        if module and hasattr(module, typ):
            driver = getattr(module, typ)
            if driver:
                return driver(name, sock)
    except:
        pass
