#      common.py
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
import uuid
import xattr
import zerorpc
from fs import edge
from conf.virtdev import PATH_MNT
from lib.util import DEFAULT_UID, zmqaddr
from conf.vdtools import PATH_VDEV, ENGINE_PORT
from lib.operations import OP_ENABLE, OP_DISABLE
from lib.modes import MODE_VIRT, MODE_VISI, MODE_CLONE, MODE_LO

def check_uuid(identity):
    try:
        return uuid.UUID(identity).hex
    except:
        return

def create(typ=None, uid=DEFAULT_UID, parent=None):
    if uid == DEFAULT_UID:
        if not typ:
            mode = MODE_VIRT
        else:
            mode = MODE_LO
        mode |= MODE_VISI
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', ENGINE_PORT))
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

def clone(parent, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        mode = MODE_CLONE
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', ENGINE_PORT))
        cli.create(uid, name, mode, None, parent, None, None, None, None, None, None, None)
        cli.close()
    else:
        attr = {'parent':parent}
        path = os.path.join(PATH_VDEV, uid)
        name = xattr.getxattr(path, 'clone:%s' % str(attr))
    return name

def combine(vrtx, timeout, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        mode = MODE_VIRT
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', ENGINE_PORT))
        cli.create(uid, name, mode, vrtx, None, None, None, None, None, None, None, timeout)
        cli.close()
    else:
        attr = {}
        attr['vertex'] = vrtx
        attr['timeout'] = timeout
        path = os.path.join(PATH_VDEV, uid)
        name = xattr.getxattr(path, 'combine:%s' % str(attr))
    return name

def enable(name, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', ENGINE_PORT))
        cli.enable(name)
        cli.close()
    else:
        path = os.path.join(PATH_VDEV, uid, name)
        xattr.setxattr(path, OP_ENABLE, '')

def disable(name, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', ENGINE_PORT))
        cli.disable(name)
        cli.close()
    else:
        path = os.path.join(PATH_VDEV, uid, name)
        xattr.setxattr(path, OP_DISABLE, '')

def link(src, dest, uid=DEFAULT_UID):
    if not check_uuid(src) or not check_uuid(dest):
        print 'invalid identity'
        return False
    if uid == DEFAULT_UID:
        path = edge.get_dir(uid, src)
    else:
        path = os.path.join(PATH_VDEV, uid, 'edge', src)
    os.system('touch %s' % os.path.join(path, dest))
    return True

def clean():
    os.system('rm -rf %s' % PATH_MNT)
