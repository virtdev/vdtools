# util.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
import sys
import ast
import uuid
import getpass
import commands
import collections
from SocketServer import ThreadingTCPServer
from vdtools.lib.attributes import ATTRIBUTES
from vdtools.conf.env import PATH_VAR, PATH_MNT
from vdtools.lib.fields import FIELDS, FIELD_DATA, ATTR, EDGE

UID_SIZE = 32
DIR_MODE = 0o755
FILE_MODE = 0o644
INFO = ['mode', 'type', 'freq', 'range']

_bin = commands.getoutput('readlink -f %s' % sys.argv[0])
_path = os.path.dirname(_bin)
_dir = os.path.dirname(_path)
sys.path.append(_dir)

_mnt = PATH_MNT
_var = PATH_VAR

def get_dir():
    return _dir

def get_cmd(op, args):
    return op + ':' + str(args)

def readlink(path):
    if path.startswith('..'):
        home = commands.getoutput('readlink -f ..')
        path = path[2:]
    elif path.startswith('.'):
        home = commands.getoutput('readlink -f %s' % path[0])
        path = path[1:]
    elif path.startswith('~'):
        user = getpass.getuser()
        if user == 'root':
            home = '/root'
        else:
            home = os.path.join('/home', user)
        path = path[1:]
    else:
        if not path.startswith('/'):
            return os.path.join(get_dir(), path)
        else:
            return path
    
    if not path.startswith('/'):
        raise Exception('Error: failed to read link')
    
    path = path[1:]
    if path.startswith('.') or path.startswith('/'):
        raise Exception('Error: failed to read link')
    
    return os.path.join(home, path)

def get_mnt_path(uid=None, name=None):
    global _mnt
    path = readlink(_mnt)
    if _mnt != path:
        _mnt = path
    if uid:
        path = os.path.join(path, uid)
        if name:
            path = os.path.join(path, name)
    return path

def get_var_path(uid=None):
    global _var
    path = readlink(_var)
    if _var != path:
        _var = path
    if uid:
        path = os.path.join(path, uid)
    return path

def get_name(ns, parent, child=None):
    if None == child:
        child = ''
    return uuid.uuid5(uuid.UUID(ns), os.path.join(str(parent), str(child))).hex

def get_devices(uid, name='', field='', sort=False):
    if not name and not field:
        path = get_var_path(uid)
    else:
        if not field:
            field = FIELD_DATA
        elif not FIELDS.get(field):
            return
        path = os.path.join(get_var_path(uid), FIELDS[field], name)
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
    path = os.path.join(get_var_path(uid), ATTR, name)
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

def save_device(manager, name, buf):
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
    if uid == UID:
        from vdtools.fs.attr import Attr
        Attr().initialize(uid, name, attr, val)

def edge_dir(uid, name):
    path = get_var_path(uid)
    return os.path.join(path, EDGE, name)

def create_server(addr, port, handler):
    server = ThreadingTCPServer((addr, port), handler, bind_and_activate=False)
    server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()
    server.serve_forever()
    
def mkdir(path):
    os.system('mkdir -p %s' % path)

def rmdir(path):
    os.system('rm -rf %s 2>/dev/null' % path)

