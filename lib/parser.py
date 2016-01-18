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
import json
from source import Source
from lib.util import DEFAULT_UID
from fs.attribute import set_attr
from lib.log import log_err, log_get
from lib.common import combine, create, clone, link
from lib.attributes import ATTR_FILTER, ATTR_HANDLER, ATTR_DISPATCHER
from dgl import DGL, get_type, get_identity, get_image, is_identity, is_image

TIMEOUT = 5 # seconds
TYPE_VDEV = 'VDev'

class Parser(object):
    def __init__(self, uid=DEFAULT_UID):
        self._uid = uid
        self._dgl = DGL()
        self._source = Source()
    
    def _create(self, name, member, parent, timeout, devices, child=False):
        if name in devices:
            return devices[name]
        
        if is_identity(name):
            identity = get_identity(name)
            devices.update({name:identity})
            return identity
        elif is_image(name):
            image = get_image(name)
            if get_type(image) == TYPE_VDEV:
                log_err(self, 'invalid type')
                raise Exception(log_get(self, 'invalid type'))
            pid = devices.get(image)
            if not pid:
                self._create(image, member, parent, timeout, devices)
                pid = devices.get(image)
                if not pid:
                    log_err(self, 'failed to create')
                    raise Exception(log_get(self, 'failed to create'))
            identity = clone(pid, uid=self._uid)
            devices.update({name:identity})
            return identity
        
        members = None
        typ = get_type(name)
        if not typ:
            log_err(self, 'invalid graph')
            raise Exception(log_get(self, 'invalid graph'))
        
        if typ == TYPE_VDEV:
            if child:
                log_err(self, 'invalid graph')
                raise Exception(log_get(self, 'invalid graph'))
            members = member.get(name)
            if members and type(members) != list:
                log_err(self, 'invalid graph')
                raise Exception(log_get(self, 'invalid graph'))
        
        if not members:
            identity = create(typ, uid=self._uid, parent=parent.get(name))
        else:
            vertex = []
            for j in members:
                identity = self._creat(j, member, parent, timeout, devices, child=True)
                if not identity:
                    log_err(self, 'invalid identity')
                    raise Exception(log_get(self, 'invalid identity'))
                vertex.append(identity)
            t = timeout.get(name)
            if not t or type(t) not in (int, float):
                t = TIMEOUT
            identity = combine(vertex, t, uid=self._uid)
            if not identity:
                log_err(self, 'failed to combine')
                raise Exception(log_get(self, 'failed to combine'))
        devices.update({name:identity})
        return identity
    
    def _parse(self, dirname, build=False, output=False):
        devices = {}
        path = os.path.join(dirname, 'graph')
        v, e = self._dgl.parse(path)
        if not v or not e:
            log_err(self, 'invalid graph')
            return
        
        path = os.path.join(dirname, 'member')
        member = self._source.get_val(path)
            
        path = os.path.join(dirname, 'parent')
        parent = self._source.get_val(path)
        
        path =  os.path.join(dirname, 'timeout')
        timeout = self._source.get_val(path)
        
        for i in v:
            if build:
                self._create(i, member, parent, timeout, devices)
        
        path = os.path.join(dirname, 'handler.py')
        handlers = self._source.get_func(path)
        
        path = os.path.join(dirname, 'filter.py')
        filters = self._source.get_func(path)
        
        path = os.path.join(dirname, 'dispatcher.py')
        dispatchers = self._source.get_func(path)
            
        if build:
            if handlers:
                for i in handlers:
                    if i in devices and not is_image(i) and not is_identity(i):
                        set_attr(self._uid, devices[i], ATTR_HANDLER, handlers[i])
            
            if filters:
                for i in filters:
                    if i in devices and not is_image(i) and not is_identity(i):
                        set_attr(self._uid, devices[i], ATTR_FILTER, filters[i])
            
            if dispatchers:
                for i in dispatchers:
                    if i in devices and not is_image(i) and not is_identity(i):
                        set_attr(self._uid, devices[i], ATTR_DISPATCHER, dispatchers[i])
            
            for i in e:
                for j in e[i]:
                    if j != i:
                        if not devices.has_key(i) or not devices.has_key(j):
                            log_err(self, 'invalid graph')
                            return
                        link(devices[i], devices[j], uid=self._uid)
            
            if output and devices:
                return json.dumps(devices)
    
    def parse(self, path):
        return self._parse(path)
    
    def build(self, path):
        return self._parse(path, build=True, output=True)
