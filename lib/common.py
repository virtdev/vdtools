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
import zerorpc
from fs import edge
from lib.util import zmqaddr
from fs.path import VDEV_FS_MOUNTPOINT
from conf.virtdev import VDEV_ENGINE_PORT, VDEV_DEFAULT_UID
from dev.vdev import VDEV_MODE_VIRT, VDEV_MODE_VISI, VDEV_MODE_ANON

def check_uuid(identity):
    try:
        return uuid.UUID(identity).hex
    except:
        return
        
def create(typ=None, vertex=None, uid=VDEV_DEFAULT_UID): 
    if not typ:
        mode = VDEV_MODE_VIRT
    else:
        mode = VDEV_MODE_ANON
    
    name = uuid.uuid4().hex
    mode |= VDEV_MODE_VISI
    if vertex:
        if type(vertex) != list:
            raise Exception('failed to create device')
        for i in vertex:
            if not check_uuid(i):
                raise Exception('failed to create device')
    if uid == VDEV_DEFAULT_UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', VDEV_ENGINE_PORT))
        cli.create(uid, name, mode, vertex, None, None, None, None, None, typ, None)
        cli.close()
    return name

def enable(name, uid=VDEV_DEFAULT_UID):
    if uid == VDEV_DEFAULT_UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', VDEV_ENGINE_PORT))
        cli.enable(name)
        cli.close()

def connect(src, dest, uid=VDEV_DEFAULT_UID):
    if not check_uuid(src) or not check_uuid(dest):
        print 'invalid identity'
        return False
    path = edge.get_dir(uid, src)
    if os.path.exists(path):
        with open(os.path.join(path, dest), 'w') as _:
            pass
        return True

def clear():
    os.system('rm -rf %s' % VDEV_FS_MOUNTPOINT)
