#      manager.py
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

from threading import Thread
from vdtools.proc.core import Core
from vdtools.proc.proc import Proc
from vdtools.dev.interface.lo import Lo
from vdtools.lib.util import DEFAULT_UID
from vdtools.conf.virtdev import PROC_ADDR, FILTER_PORT, HANDLER_PORT, DISPATCHER_PORT

class Manager(object):
    def _init_proc(self):
        self._filter = Proc(self, PROC_ADDR, FILTER_PORT)
        self._handler = Proc(self, PROC_ADDR, HANDLER_PORT)
        self._dispatcher = Proc(self, PROC_ADDR, DISPATCHER_PORT)
        self._filter.start()
        self._handler.start()
        self._dispatcher.start()
    
    def _init_dev(self):
        self.devices = []
        self._lo = Lo(self.uid, self.core)
        self.devices.append(self._lo)
    
    def _init_core(self):
        self.core = Core(self)
    
    def _initialize(self):
        self._init_proc()
        self._init_core()
        self._init_dev()
    
    def __init__(self):
        self.channel = None
        self._active = False
        self.uid = DEFAULT_UID
        self._initialize()
    
    def _start(self):
        for device in self.devices:
            device.start()
    
    def start(self):
        if not self._active:
            Thread(target=self._start).start()
            self._active = True
    
    def create(self, device, init):
        return self._lo.create(device, init)
    
    @property
    def compute_unit(self):
        pass
