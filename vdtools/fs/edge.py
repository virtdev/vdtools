#      edge.py
#      
#      Copyright (C) 2016 Yi-Wei Ci <ciyiwei@hotmail.com>
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
from vdtools.lib.fields import EDGE
from vdtools.conf.env import PATH_VAR

class Edge(object):
    def _get_path(self, uid, edge, hidden):
        if not hidden:
            return str(os.path.join(PATH_VAR, uid, EDGE, edge[0], edge[1]))
        else:
            return str(os.path.join(PATH_VAR, uid, EDGE, edge[0], '.' + edge[1]))
    
    def initialize(self, uid, edge, hidden=False):
        path = self._get_path(uid, edge, hidden)
        if not os.path.exists(path):
            with open(path, 'w') as _:
                pass
