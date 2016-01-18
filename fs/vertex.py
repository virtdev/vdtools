#      vertex.py
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
from lib.domains import VERTEX
from conf.virtdev import PATH_FS

class Vertex(object):
    def _get_path(self, uid, name, vertex):
        return str(os.path.join(PATH_FS, uid, VERTEX, name, vertex))
    
    def initialize(self, uid, name, vertex):
        for i in vertex:
            path = self._get_path(uid, name, i)
            if not os.path.exists(path):
                with open(path, 'w') as _:
                    pass
