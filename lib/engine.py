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
from dev.udo import UDO
from util import zmqaddr
from fs.attr import Attr
from fs.data import Data
from fs.edge import Edge
from lib.op import OP_OPEN
from fs.vertex import Vertex
from threading import Thread
from lib.util import load_driver
from dev.manager import Manager
from conf.virtdev import ENGINE_PORT
from lib.mode import MODE_LO, MODE_VIRT
from dev.interfaces.lo import device_name
from fs.attr import ATTR_MODE, ATTR_FREQ, ATTR_FILTER, ATTR_HANDLER, ATTR_PROFILE, ATTR_DISPATCHER

class EnginInterface(object):
    def __init__(self, manager):
        self._attr = Attr()
        self._data = Data()
        self._edge = Edge()
        self._vertex = Vertex()
        self._manager = manager
        self._manager.start()
    
    def enable(self, name):
        for d in self._manager.devices:
            dev = d.find(name)
            if dev:
                dev.proc(name, OP_OPEN)
    
    def create(self, uid, name, mode, vertex, parent, freq, prof, hndl, filt, disp, typ):
        lo = mode & MODE_LO
        if lo and not typ:
            log_err(self, 'failed to create device, invalid device')
            raise Exception('ailed to create device')
        
        if not prof:
            if lo:
                driver = load_driver(typ)
                if not driver:
                    log_err(self, 'failed to create device')
                    raise Exception('failed to create device')
                mode = driver.get_mode()
                freq = driver.get_freq()
                prof = driver.get_profile()
            elif mode & MODE_VIRT:
                prof = UDO().d_profile
        
        self._data.initialize(uid, name)
        self._attr.initialize(uid, name, {ATTR_MODE:mode})
        
        if freq:
            self._attr.initialize(uid, name, {ATTR_FREQ:freq})
        
        if filt:
            self._attr.initialize(uid, name, {ATTR_FILTER:filt})
        
        if hndl:
            self._attr.initialize(uid, name, {ATTR_HANDLER:hndl})
        
        if prof:
            self._attr.initialize(uid, name, {ATTR_PROFILE:prof})
        
        if disp:
            self._attr.initialize(uid, name, {ATTR_DISPATCHER:disp})
        
        if vertex:
            self._vertex.initialize(uid, name, vertex)
            for v in vertex:
                self._edge.initialize(uid, (v, name), hidden=True)
        
        if lo:
            self._manager.create(device_name(typ, name), init=False)

class Engine(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._manager = Manager()
    
    def run(self):
        srv = zerorpc.Server(EnginInterface(self._manager))
        srv.bind(zmqaddr('127.0.0.1', ENGINE_PORT))
        srv.run()
