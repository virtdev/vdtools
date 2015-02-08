#      path.py
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
from conf.virtdev import VDEV_FS_MOUNTPOINT

VDEV_FS_LABELS = {'vertex':'vertex', 'edge':'edge', 'data':'data', 'attr':'attr', 'temp':'temp'}

def is_local(uid, name):
    path = os.path.join(VDEV_FS_MOUNTPOINT, uid, 'data', name)
    return os.path.exists(path)

def load(uid, name='', label='data', sort=False):
    if not name and not label:
        path = os.path.join(VDEV_FS_MOUNTPOINT, uid)
    else:
        if label not in VDEV_FS_LABELS.keys():
            return
        path = os.path.join(VDEV_FS_MOUNTPOINT, uid, VDEV_FS_LABELS[label], name)
    if not os.path.exists(path):
        return
    if not sort:
        return os.listdir(path)
    else:
        key = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return sorted(os.listdir(path), key=key)

