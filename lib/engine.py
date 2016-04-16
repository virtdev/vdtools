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
from fs.data import Data
from fs.edge import Edge
from fs.vrtx import Vrtx
from fs.attr import Attr
from threading import Thread
from lib.loader import Loader
from dev.manager import Manager
from lib.util import load_driver
from conf.vdtools import ENGINE_PORT
from dev.interfaces.lo import device_name
from lib.operations import OP_OPEN, OP_CLOSE
from lib.modes import MODE_LO, MODE_VIRT, MODE_CLONE
from lib.attributes import ATTR_MODE, ATTR_FREQ, ATTR_FILTER, ATTR_HANDLER, ATTR_PROFILE, ATTR_DISPATCHER, ATTR_PARENT, ATTR_TIMEOUT

TYPE_VDEV = 'VDev'

class EnginInterface(object):
    def __init__(self, manager):
        self._data = Data()
        self._edge = Edge()
        self._attr = Attr()
        self._vrtx = Vrtx()
        self._manager = manager
        self._manager.start()
    
    def enable(self, name):
        for d in self._manager.devices:
            dev = d.find(name)
            if dev:
                dev.proc(name, OP_OPEN)
    
    def disable(self, name):
        for d in self._manager.devices:
            dev = d.find(name)
            if dev:
                dev.proc(name, OP_CLOSE)
    
    def create(self, uid, name, mode, vrtx, parent, freq, prof, hndl, filt, disp, typ, timeout):
        lo = mode & MODE_LO
        if lo and not typ:
            log_err(self, 'failed to create device, invalid device')
            raise Exception('Error: failed to create device')
        
        if mode & MODE_CLONE:
            if not parent:
                log_err(self, 'failed to create device, no parent')
                raise Exception('Error: failed to create device')
            prof = Loader(uid).get_profile(parent)
            typ = prof['type']
        
        if not mode & MODE_VIRT:
            timeout = None
        
        if mode & MODE_VIRT:
            typ = TYPE_VDEV
        
        if not prof:
            if typ:
                driver = load_driver(typ)
                if not driver:
                    log_err(self, 'failed to create device')
                    raise Exception('Error: failed to create device')
                if mode & MODE_CLONE:
                    mode = driver.get_mode() | MODE_CLONE
                else:
                    mode = driver.get_mode()
                freq = driver.get_freq()
                prof = driver.get_profile()
        
        self._data.initialize(uid, name)
        self._attr.initialize(uid, name, ATTR_MODE, mode)
        
        if freq:
            self._attr.initialize(uid, name, ATTR_FREQ, freq)
        
        if filt:
            self._attr.initialize(uid, name, ATTR_FILTER, filt)
        
        if hndl:
            self._attr.initialize(uid, name, ATTR_HANDLER, hndl)
        
        if prof:
            self._attr.initialize(uid, name, ATTR_PROFILE, prof)
        
        if mode & MODE_CLONE:
            self._attr.initialize(uid, name, ATTR_PARENT, parent)
        
        if disp:
            self._attr.initialize(uid, name, ATTR_DISPATCHER, disp)
        
        if timeout:
            self._attr.initialize(uid, name, ATTR_TIMEOUT, timeout)
        
        if vrtx:
            if mode & MODE_CLONE:
                log_err(self, 'failed to create device, invalid vertex')
                raise Exception('Error: failed to create device')
            self._vrtx.initialize(uid, name, vrtx)
            for v in vrtx:
                self._edge.initialize(uid, (v, name), hidden=True)
        
        if lo:
            self._manager.create(device_name(typ, name, mode), init=False)

class Engine(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._manager = Manager()
    
    def run(self):
        srv = zerorpc.Server(EnginInterface(self._manager))
        srv.bind(zmqaddr('127.0.0.1', ENGINE_PORT))
        srv.run()
