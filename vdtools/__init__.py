# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
import uuid
import xattr
import zerorpc
from vdtools.conf.user import UID
from vdtools.conf.defaults import *
from vdtools.conf.env import PATH_VDEV
from vdtools.lib.simulator import Simulator
from vdtools.lib.modes import MODE_VIRT, MODE_CLONE
from vdtools.lib.operations import OP_ENABLE, OP_DISABLE
from vdtools.lib.util import zmqaddr, edge_dir, close_port, get_mnt_path

def check_uuid(identity):
    try:
        return uuid.UUID(identity).hex
    except:
        return

def create(typ, uid=UID, parent=None):
    if uid == UID:
        mode = MODE_VIRT
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, None, None, None, None, None, None, None, typ, None)
        cli.close()
    else:
        attr = {}
        attr['type'] = typ
        if parent:
            attr['parent'] = parent
        path = os.path.join(PATH_VDEV, uid)
        name = xattr.getxattr(path, 'create:%s' % str(attr))
    return name

def clone(parent, uid=UID):
    if uid == UID:
        mode = MODE_CLONE
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, None, parent, None, None, None, None, None, None, None)
        cli.close()
    else:
        attr = {'parent':parent}
        path = os.path.join(PATH_VDEV, uid)
        name = xattr.getxattr(path, 'clone:%s' % str(attr))
    return name

def combine(vrtx, timeout, uid=UID):
    if uid == UID:
        mode = MODE_VIRT
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, vrtx, None, None, None, None, None, None, None, timeout)
        cli.close()
    else:
        attr = {}
        attr['vertex'] = vrtx
        attr['timeout'] = timeout
        path = os.path.join(PATH_VDEV, uid)
        name = xattr.getxattr(path, 'combine:%s' % str(attr))
    return name

def enable(name, uid=UID):
    if uid == UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.enable(name)
        cli.close()
    else:
        path = os.path.join(PATH_VDEV, uid, name)
        xattr.setxattr(path, OP_ENABLE, '')

def disable(name, uid=UID):
    if uid == UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.disable(name)
        cli.close()
    else:
        path = os.path.join(PATH_VDEV, uid, name)
        xattr.setxattr(path, OP_DISABLE, '')

def link(src, dest, uid=UID):
    if not check_uuid(src) or not check_uuid(dest):
        print 'invalid identity'
        return False
    if uid == UID:
        path = edge_dir(uid, src)
    else:
        path = os.path.join(PATH_VDEV, uid, 'edge', src)
    os.system('touch %s' % os.path.join(path, dest))
    return True

def clean():
    os.system('rm -rf %s' % get_mnt_path())

def initialize():
    path = get_mnt_path()
    if not os.path.exists(path):
        os.makedirs(path, 0o755)
    close_port(LO_PORT)
    close_port(FILTER_PORT)
    close_port(HANDLER_PORT)
    close_port(DISPATCHER_PORT)
    simu = Simulator()
    simu.start()
    simu.join()
