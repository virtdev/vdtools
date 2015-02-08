#      mount.py
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
from lib.util import close_port
from lib.engine import VDevEngine
from conf.virtdev import VDEV_LO_PORT, VDEV_MAPPER_PORT, VDEV_HANDLER_PORT, VDEV_DISPATCHER_PORT, VDEV_FS_MOUNTPOINT

def _clean():
    close_port(VDEV_LO_PORT)
    close_port(VDEV_MAPPER_PORT)
    close_port(VDEV_HANDLER_PORT)
    close_port(VDEV_DISPATCHER_PORT)

def mount():
    if not os.path.exists(VDEV_FS_MOUNTPOINT):
        os.makedirs(VDEV_FS_MOUNTPOINT, 0o755)
    _clean()
    engine = VDevEngine()
    engine.start()
    engine.join()
    
    