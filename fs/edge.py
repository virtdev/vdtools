#      edge.py
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
from path import DOMAIN
from conf.virtdev import FS_PATH, MOUNTPOINT

def get_dir(uid, name):
    return os.path.join(MOUNTPOINT, uid, DOMAIN['edge'], name)

class Edge(object):
    def _get_path(self, uid, edge):
        return str(os.path.join(FS_PATH, uid, 'edge', edge[0], edge[1]))
    
    def initialize(self, uid, edge):
        path = self._get_path(uid, edge)
        if not os.path.exists(path):
            with open(path, 'w') as _:
                pass
    