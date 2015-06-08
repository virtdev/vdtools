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
from conf.virtdev import DEFAULT_UID
from lib.common import combine, create, link
from fs.attr import ATTR_FILTER, ATTR_HANDLER, ATTR_DISPATCHER, set_attr

TIMEOUT = 5 # seconds
TYPE_VDEV = 'VDev'

class Parser(object):
    def __init__(self, uid=DEFAULT_UID):
        self._uid = uid
        self._graph = Graph()
        self._source = Source()
    
    def _parse(self, path, build=False):
        names = {}
        virtual = []
        devices = []
        name = os.path.join(path, 'graph')
        v, e = self._graph.parse(name)
        if not v or not e:
            log_err(self, 'invalid graph')
            return
        
        path_device = os.path.join(path, 'device')
        source_device = self._source.get_val(path_device)
        path_timeout =  os.path.join(path, 'timeout')
        source_timeout = self._source.get_val(path_timeout)
        for i in v:
            if self._graph.has_type(i):
                members = None
                typ = self._graph.get_type(i)
                
                if not typ:
                    log_err(self, 'invalid graph')
                    return
                
                if i in devices:
                    continue
                
                if typ == TYPE_VDEV:
                    members = source_device.get(i)
                    if members and type(members) != list:
                        log_err(self, 'invalid graph')
                        return
                
                n = None
                if not members:
                    if build:
                        n = create(typ, uid=self._uid)
                else:
                    vertex = []
                    timeout = source_timeout.get(i)
                    if not timeout or type(timeout) not in (int, float):
                        timeout = TIMEOUT
                    for j in members:
                        if self._graph.has_type(j):
                            typ = self._graph.get_type(j)
                            if build:
                                n = create(typ, uid=self._uid)
                            vertex.append(n)
                        else:
                            vertex.append(self._graph.get_identity(j))
                    if build:
                        n = combine(vertex, timeout, uid=self._uid)
                    virtual.append(i)
                
                devices.append(i)
                names.update({i:n})
            else:
                names.update({i:self._get_identity(i)})
        
        path_handler = os.path.join(path, 'handler.py')
        handlers = self._source.get_func(path_handler)
        if handlers and build:
            for i in handlers:
                if i in devices:
                    set_attr(self._uid, names[i], ATTR_HANDLER, handlers[i])
        
        path_filter = os.path.join(path, 'filter.py')
        filters = self._source.get_func(path_filter)
        if filters and build:
            for i in filters:
                if i in virtual:
                    set_attr(self._uid, names[i], ATTR_FILTER, filters[i])
        
        path_dispatcher = os.path.join(path, 'dispatcher.py')
        dispatchers = self._source.get_func(path_dispatcher)
        if dispatchers and build:
            for i in dispatchers:
                if i in devices:
                    set_attr(self._uid, names[i], ATTR_DISPATCHER, dispatchers[i])
        
        for i in e:
            for j in e[i]:
                if j != i:
                    if not names.has_key(i) or not names.has_key(j):
                        log_err(self, 'invalid graph')
                        return
                    if build:
                        link(names[i], names[j], uid=self._uid)
        return True
    
    def parse(self, path):
        return self._parse(path, build=False)
    
    def build(self, path):
        return self._parse(path, build=True)
