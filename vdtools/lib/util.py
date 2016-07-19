#      util.py
#      
#      Copyright (C) 2016 Yi-Wei Ci <ciyiwei@hotmail.com>
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
import uuid
import commands
import collections
from vdtools.fs.attr import Attr
from vdtools.conf.env import PATH_VAR
from SocketServer import ThreadingTCPServer
from vdtools.lib.attributes import ATTRIBUTES
from vdtools.lib.fields import FIELDS, FIELD_DATA, ATTR, EDGE

UID_SIZE = 32
DEFAULT_UID = ''
DIR_MODE = 0o755
FILE_MODE = 0o644

DEVNULL = open(os.devnull, 'wb')
INFO = ['mode', 'type', 'freq', 'range']

def get_dir():
    return _dir

def get_name(ns, parent, child=None):
    if None == child:
        child = ''
    return uuid.uuid5(uuid.UUID(ns), os.path.join(str(parent), str(child))).hex

def get_devices(uid, name='', field='', sort=False):
    if not name and not field:
        path = os.path.join(PATH_VAR, uid)
    else:
        if not field:
            field = FIELD_DATA
        elif not FIELDS.get(field):
            return
        path = os.path.join(PATH_VAR, uid, FIELDS[field], name)
    if not os.path.exists(path):
        return
    if not sort:
        return os.listdir(path)
    else:
        key = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return sorted(os.listdir(path), key=key)

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
    path = os.path.join(PATH_VAR, uid, ATTR, name)
    return os.path.exists(path)

def zmqaddr(addr, port):
    return 'tcp://%s:%d' % (str(addr), int(port))

def close_port(port):
    cmd = 'lsof -i:%d -Fp | cut -c2- | xargs --no-run-if-empty kill -9 2>/dev/null' % port
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

def edge_lock(func):
    def _edge_lock(*args, **kwargs):
        self = args[0]
        edge = args[1]
        self._lock.acquire(edge[0])
        try:
            return func(*args, **kwargs)
        finally:
            self._lock.release(edge[0])
    return _edge_lock

def mount_device(uid, name, mode, freq, prof):
    pass

def device_sync(manager, name, buf):
    pass

def device_info(buf):
    try:
        info = ast.literal_eval(buf)
        if type(info) != dict:
            return
        for i in info:
            for j in info[i].keys():
                if j not in INFO:
                    return
        return info
    except:
        pass

def set_attr(uid, name, attr, val):
    if attr not in ATTRIBUTES:
        return
    if uid == DEFAULT_UID:
        Attr().initialize(uid, name, attr, val)

def edge_dir(uid, name):
    return os.path.join(PATH_VAR, uid, EDGE, name)

def create_server(addr, port, handler):
    server = ThreadingTCPServer((addr, port), handler, bind_and_activate=False)
    server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()
    server.serve_forever()
