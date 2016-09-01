# simulator.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import zerorpc
from threading import Thread
from vdtools.fs.data import Data
from vdtools.fs.edge import Edge
from vdtools.fs.vrtx import Vrtx
from vdtools.fs.attr import Attr
from vdtools.lib.modes import *
from vdtools.lib.operations import *
from vdtools.lib.attributes import *
from vdtools.lib.log import log_err
from vdtools.lib.util import zmqaddr
from vdtools.lib.loader import Loader
from vdtools.dev.manager import Manager
from vdtools.dev.driver import load_driver
from vdtools.dev.interface.lo import device_name
from vdtools.conf.defaults import SIMULATOR_PORT

class SimulatorInterface(object):
    def __init__(self, manager):
        self._data = Data()
        self._edge = Edge()
        self._attr = Attr()
        self._vrtx = Vrtx()
        self._manager = manager
        manager.start()
    
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
        if not typ:
            log_err(self, 'failed to create device, no type')
            raise Exception('Error: failed to create device')
        
        if mode & MODE_CLONE:
            if not parent:
                log_err(self, 'failed to create device, no parent')
                raise Exception('Error: failed to create device')
            prof = Loader(uid).get_profile(parent)
            typ = prof['type']
        
        if not mode & MODE_VIRT:
            timeout = None
        
        if not prof:
            if typ:
                driver = load_driver(typ)
                if not driver:
                    log_err(self, 'failed to create device, no driver')
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
        
        if disp:
            self._attr.initialize(uid, name, ATTR_DISPATCHER, disp)
        
        if timeout:
            self._attr.initialize(uid, name, ATTR_TIMEOUT, timeout)
        
        if mode & MODE_CLONE:
            self._attr.initialize(uid, name, ATTR_PARENT, parent)
        
        if vrtx:
            if mode & MODE_CLONE:
                log_err(self, 'failed to create device, cannot set vertex for a cloned device')
                raise Exception('Error: failed to create device')
            self._vrtx.initialize(uid, name, vrtx)
            for v in vrtx:
                self._edge.initialize(uid, (v, name), hidden=True)
        
        self._manager.create(device_name(typ, name, mode), init=False)

class Simulator(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._manager = Manager()
    
    def run(self):
        srv = zerorpc.Server(SimulatorInterface(self._manager))
        srv.bind(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        srv.run()
