#      engine.py
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

import zerorpc
from log import log_err
from util import zmqaddr
from fs.attr import Attr
from fs.data import Data
from fs.edge import Edge
from fs.vertex import Vertex
from threading import Thread
from dev.lo import get_device
from fs.manager import VDevFSManager
from dev.interface import load_device
from conf.virtdev import VDEV_ENGINE_PORT
from dev.vdev import VDEV_MODE_ANON, VDEV_MODE_VIRT, VDEV_OPEN, VDev
from fs.attr import VDEV_ATTR_MODE, VDEV_ATTR_FREQ, VDEV_ATTR_MAPPER, VDEV_ATTR_HANDLER, VDEV_ATTR_PROFILE, VDEV_ATTR_DISPATCHER

class VDevEnginInterface(object):
    def __init__(self, manager):
        self._attr = Attr()
        self._data = Data()
        self._edge = Edge()
        self._vertex = Vertex()
        self.manager = manager
        self.manager.start()
    
    def enable(self, name):
        for d in self.manager.devices:
            dev = d.find(name)
            if dev:
                dev.proc(name, VDEV_OPEN)
    
    def create(self, uid, name, mode, vertex, freq, profile, handler, mapper, dispatcher, typ, parent):
        anon = mode & VDEV_MODE_ANON
        if anon and not typ:
            log_err(self, 'failed to create device, invalid device')
            raise Exception('ailed to create device')
        
        if not profile:
            if anon:
                dev = load_device(typ)
                mode = dev.d_mode
                profile = dev.d_profile
            elif mode & VDEV_MODE_VIRT:
                profile = VDev().d_profile
        
        self._data.initialize(uid, name)
        self._attr.initialize(uid, name, {VDEV_ATTR_MODE:mode})
        
        if freq:
            self._attr.initialize(uid, name, {VDEV_ATTR_FREQ:freq})
        
        if mapper:
            self._attr.initialize(uid, name, {VDEV_ATTR_MAPPER:mapper})
        
        if handler:
            self._attr.initialize(uid, name, {VDEV_ATTR_HANDLER:handler})
        
        if profile:
            self._attr.initialize(uid, name, {VDEV_ATTR_PROFILE:profile})
        
        if dispatcher:
            self._attr.initialize(uid, name, {VDEV_ATTR_DISPATCHER:dispatcher})
        
        if vertex:
            self._vertex.initialize(uid, name, vertex)
            for v in vertex:
                self._edge.initialize(uid, (v, name), hidden=True)
        
        if anon:
            self.manager.lo.register(get_device(typ, name), init=False)

class VDevEngine(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.manager = VDevFSManager()
    
    def run(self):
        srv = zerorpc.Server(VDevEnginInterface(self.manager))
        srv.bind(zmqaddr('127.0.0.1', VDEV_ENGINE_PORT))
        srv.run()
