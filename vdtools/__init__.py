# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
import uuid
import xattr
import zerorpc
from vdtools.lib.api import *
from vdtools.conf.user import UID
from vdtools.conf.defaults import *
from vdtools.conf.env import PATH_MNT
from vdtools.lib.simulator import Simulator
from vdtools.lib.modes import MODE_VIRT, MODE_CLONE
from vdtools.lib.util import zmqaddr, edge_dir, close_port, get_mnt_path, mkdir, rmdir, check_uuid

def create(device_type, parent=None, uid=UID, path=PATH_MNT):
    if uid == UID:
        mode = MODE_VIRT
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, None, None, None, None, None, None, None, device_type, None)
        cli.close()
    else:
        path = os.path.join(path, uid)
        if parent:
            name = api_create(path, type=device_type, parent=parent)
        else:
            name = api_create(path, type=device_type)
    return name

def clone(parent, uid=UID, path=PATH_MNT):
    if uid == UID:
        mode = MODE_CLONE
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, None, parent, None, None, None, None, None, None, None)
        cli.close()
    else:
        path = os.path.join(path, uid)
        name = api_clone(path, parent=parent)
    return name

def combine(device_type, vertex, timeout, uid=UID, path=PATH_MNT):
    if uid == UID:
        mode = MODE_VIRT
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, vertex, None, None, None, None, None, None, device_type, timeout)
        cli.close()
    else:
        path = os.path.join(path, uid)
        name = api_combine(path, type=device_type, vertex=vertex, timeout=timeout)
    return name

def enable(name, uid=UID, path=PATH_MNT):
    if uid == UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.enable(name)
        cli.close()
    else:
        path = os.path.join(path, uid, name)
        api_enable(path)

def disable(name, uid=UID, path=PATH_MNT):
    if uid == UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.disable(name)
        cli.close()
    else:
        path = os.path.join(path, uid, name)
        api_disable(path)

def link(src, dest, uid=UID, path=PATH_MNT):
    if not check_uuid(src) or not check_uuid(dest):
        return False
    if uid == UID:
        path = edge_dir(uid, src)
    else:
        path = os.path.join(path, uid, 'edge', src)
    path = os.path.join(path, dest)
    api_touch(path)
    return True

def clean():
    path = get_mnt_path()
    rmdir(path)

def initialize():
    path = get_mnt_path()
    mkdir(path)
    close_port(LO_PORT)
    close_port(FILTER_PORT)
    close_port(HANDLER_PORT)
    close_port(DISPATCHER_PORT)
    simu = Simulator()
    simu.start()
    simu.join()
