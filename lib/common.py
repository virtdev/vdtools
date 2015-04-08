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
from lib.mode import MODE_VIRT, MODE_VISI, MODE_LO
from conf.virtdev import MOUNTPOINT, ENGINE_PORT, DEFAULT_UID

def check_uuid(identity):
    try:
        return uuid.UUID(identity).hex
    except:
        return
        
def create(typ=None, uid=DEFAULT_UID): 
    if not typ:
        mode = MODE_VIRT
    else:
        mode = MODE_LO
    
    name = uuid.uuid4().hex
    mode |= MODE_VISI
    if uid == DEFAULT_UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', ENGINE_PORT))
        cli.create(uid, name, mode, None, None, None, None, None, None, None, typ)
        cli.close()
    return name

def enable(name, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', ENGINE_PORT))
        cli.enable(name)
        cli.close()

def associate(src, dest, uid=DEFAULT_UID):
    if not check_uuid(src) or not check_uuid(dest):
        print 'invalid identity'
        return False
    path = edge.get_dir(uid, src)
    if os.path.exists(path):
        with open(os.path.join(path, dest), 'w') as _:
            pass
        return True

def clear():
    os.system('rm -rf %s' % MOUNTPOINT)
