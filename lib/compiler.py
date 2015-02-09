#      compiler.py
#      
#      Copyright (C) 2015 Yi-Wei Ci <ciyiwei@hotmail.com>
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
from graph import VDGraph
from source import VDSource
from lib.log import log_err
from lib.common import create, connect
from conf.virtdev import VDEV_DEFAULT_UID
from fs.attr import VDEV_ATTR_MAPPER, VDEV_ATTR_HANDLER, VDEV_ATTR_DISPATCHER, set_attr

class VDCompiler(object):
    def __init__(self, uid=VDEV_DEFAULT_UID):
        self._uid = uid
        self._graph = VDGraph()
        self._source = VDSource()
    
    def compile(self, path):
        names = {}
        name = os.path.join(path, 'graph')
        v, e = self._graph.parse(name)
        if not v or not e:
            log_err(self, 'invalid graph')
            return
        
        for i in v:
            if not self._graph.is_virtual_vertex(i):
                typ = self._graph.get_vertex_type(i)
                if not typ:
                    log_err(self, 'invalid graph')
                    return
        
        for i in v:
            if self._graph.is_virtual_vertex(i):
                n = create(uid=self._uid)
            else:
                typ = self._graph.get_vertex_type(i)
                n = create(typ, uid=self._uid)
            names.update({i:n})
        
        name = os.path.join(path, 'handler.py')
        handlers = self._source.parse(name)
        if handlers:
            for i in handlers:
                if self._graph.is_virtual_vertex(i) and i in v:
                    set_attr(self._uid, names[i], {VDEV_ATTR_HANDLER:handlers[i]})
        
        name = os.path.join(path, 'mapper.py')
        mappers = self._source.parse(name)
        if mappers:
            for i in mappers:
                if self._graph.is_virtual_vertex(i) and i in v:
                    set_attr(self._uid, names[i], {VDEV_ATTR_MAPPER:mappers[i]})
        
        name = os.path.join(path, 'dispatcher.py')
        dispatchers = self._source.parse(name)
        if dispatchers:
            for i in dispatchers:
                if self._graph.is_virtual_vertex(i) and i in v:
                    set_attr(self._uid, names[i], {VDEV_ATTR_DISPATCHER:dispatchers[i]})
        
        for i in e:
            for j in e[i]:
                if j != i:
                    connect(names[i], names[j], self._uid)
        
        return True
