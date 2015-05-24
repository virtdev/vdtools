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
import ast
import imp
import uuid
import struct

UID_SIZE = 32
DEFAULT_UID = '0' * UID_SIZE
INFO_FIELDS = ['mode', 'type', 'freq', 'range']

DIR_MODE = 0o755
FILE_MODE = 0o644

DEVNULL = open(os.devnull, 'wb')
DRIVER_PATH = os.path.join(os.getcwd(), 'drivers')

def zmqaddr(addr, port):
    return 'tcp://%s:%d' % (str(addr), int(port))

def srv_start(srv_list):
    for srv in srv_list:
        srv.start()

def srv_join(srv_list):
    for srv in srv_list:
        srv.join()

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
            raise Exception('failed to receive')
        ret.append(buf)
        length -= len(buf) 
    return ''.join(ret)

def recv_pkt(sock):
    head = recv_bytes(sock, 4)
    if not head:
        return ''
    length = struct.unpack('I', head)[0]
    return recv_bytes(sock, length)

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

def get_name(ns, parent, child=None):
    if None == child:
        child = ''
    return uuid.uuid5(uuid.UUID(ns), os.path.join(str(parent), str(child))).hex

def hash_name(name):
    length = len(name)
    if length > 1:
        return (ord(name[-2]) << 8) + ord(name[-1])
    elif length == 1:
        return ord(name[-1])
    else:
        return 0

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

def load_driver(typ, name=None, setup=False):
    try:
        module = imp.load_source(typ, os.path.join(DRIVER_PATH, '%s.py' % typ.lower()))
        if module and hasattr(module, typ):
            driver = getattr(module, typ)
            if driver:
                return driver(name=name, setup=setup)
    except:
        pass

def info(typ, mode=0, freq=None, rng=None):
    ret = {'type':typ, 'mode':mode}
    if freq:
        ret.update({'freq':freq})
    if range:
        ret.update({'range':rng})
    return ret

def check_info(buf):
    try:
        info = ast.literal_eval(buf)
        if type(info) != dict:
            return
        for i in info:
            for j in info[i].keys():
                if j not in INFO_FIELDS:
                    return
        return info
    except:
        pass

def check_profile(buf):
    prof = {}
    for item in buf:
        pair = item.strip().split('=')
        if len(pair) != 2:
            raise Exception('invalid profile')
        if pair[0] == 'type':
            prof.update({'type':str(pair[1])})
        elif pair[0] == 'range':
            r = ast.literal_eval(pair[1])
            if type(r) != dict:
                raise Exception('invalid profile')
            prof.update({'range':r})
        elif pair[0] == 'index':
            if pair[1] == 'None':
                prof.update({'index':None})
            else:
                prof.update({'index':int(pair[1])})
    if not prof.has_key('type'):
        raise Exception('invalid profile')
    return prof
