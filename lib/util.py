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
import sys
import ast
import imp
import uuid
import struct
import commands
import collections
from domains import DOMAINS, DATA, ATTRIBUTE

UID_SIZE = 32
DEFAULT_UID = ''
INFO_FIELDS = ['mode', 'type', 'freq', 'range']

DIR_MODE = 0o755
FILE_MODE = 0o644

DEVNULL = open(os.devnull, 'wb')

_path = commands.getoutput('readlink -f %s' % sys.argv[0])
_dir = os.path.dirname(_path)
sys.path.append(_dir)
DRIVER_PATH = os.path.join(_dir, 'drivers')
from conf.virtdev import PATH_FS, PATH_MOUNTPOINT

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

def load_driver(typ, name=None):
    try:
        driver_name = typ.lower()
        module = imp.load_source(typ, os.path.join(DRIVER_PATH, driver_name, '%s.py' % driver_name))
        if module and hasattr(module, typ):
            driver = getattr(module, typ)
            if driver:
                return driver(name=name)
    except:
        pass

def device_info(buf):
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

def unicode2str(buf):
    if isinstance(buf, basestring):
        return str(buf)
    elif isinstance(buf, collections.Mapping):
        return dict(map(unicode2str, buf.iteritems()))
    elif isinstance(buf, collections.Iterable):
        return type(buf)(map(unicode2str, buf))
    else:
        return buf

def is_local(uid, name):
    path = os.path.join(PATH_FS, uid, ATTRIBUTE, name)
    return os.path.exists(path)

def member_list(uid, name='', domain='', sort=False, passthrough=False):
    if not passthrough:
        root = PATH_MOUNTPOINT
    else:
        root = PATH_FS
    if not name and not domain:
        path = os.path.join(root, uid)
    else:
        if domain and domain not in DOMAINS:
            return
        if passthrough:
            if domain:
                domain = DOMAINS[domain]
            else:
                domain = DATA
        path = os.path.join(root, uid, domain, name)
    if not os.path.exists(path):
        return
    if not sort:
        return os.listdir(path)
    else:
        key = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return sorted(os.listdir(path), key=key)

def device_sync(manager, name, buf):
    pass
