#      parser.py
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
from graph import Graph
from source import Source
from lib.log import log_err
from lib.common import create, link
from conf.virtdev import DEFAULT_UID
from fs.attr import ATTR_FILTER, ATTR_HANDLER, ATTR_DISPATCHER, set_attr

class Parser(object):
    def __init__(self, uid=DEFAULT_UID):
        self._uid = uid
        self._graph = Graph()
        self._source = Source()
    
    def parse(self, path):
        names = {}
        devices = []
        name = os.path.join(path, 'graph')
        v, e = self._graph.parse(name)
        if not v or not e:
            log_err(self, 'invalid graph')
            return
        
        for i in v:
            if self._graph.has_type(i):
                typ = self._graph.get_type(i)
                if not typ:
                    log_err(self, 'invalid graph')
                    return
        
        for i in v:
            if self._graph.has_type(i):
                typ = self._graph.get_type(i)
                n = create(typ, uid=self._uid)
                device = self._graph.get_device(i)
                if device and device not in devices:
                    devices.append(device)
                    names.update({device:n})
            else:
                names.update({i:i})
        
        name = os.path.join(path, 'handler.py')
        handlers = self._source.parse(name)
        if handlers:
            for i in handlers:
                if i in devices:
                    set_attr(self._uid, names[i], ATTR_HANDLER, handlers[i])
        
        name = os.path.join(path, 'filter.py')
        filters = self._source.parse(name)
        if filters:
            for i in filters:
                if i in devices:
                    set_attr(self._uid, names[i], ATTR_FILTER, filters[i])
        
        name = os.path.join(path, 'dispatcher.py')
        dispatchers = self._source.parse(name)
        if dispatchers:
            for i in dispatchers:
                if i in devices:
                    set_attr(self._uid, names[i], ATTR_DISPATCHER, dispatchers[i])
        
        for i in e:
            for j in e[i]:
                if j != i:
                    if self._graph.has_type(i):
                        src = self._graph.get_device(i)
                    else:
                        src = i
                    if self._graph.has_type(j):
                        dest = self._graph.get_device(j)
                    else:
                        dest = j
                    if not names.has_key(src) or not names.has_key(dest):
                        log_err(self, 'invalid graph')
                        return
                    link(names[src], names[dest], self._uid)
        return True
