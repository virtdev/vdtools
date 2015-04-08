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

from lo import VDevLo
from threading import Thread
from proc.sandbox import VDevSandbox
from proc.synchronizer import VDevSynchronizer
from conf.virtdev import FILTER_PORT, HANDLER_PORT, DISPATCHER_PORT, DEFAULT_UID

class VDevManager(object):
    def _init_sandbox(self):
        self._filter = VDevSandbox(FILTER_PORT)
        self._handler = VDevSandbox(HANDLER_PORT)
        self._dispatcher = VDevSandbox(DISPATCHER_PORT)
        self._filter.start()
        self._handler.start()
        self._dispatcher.start()
    
    def _init_dev(self):
        self.devices = []
        self.lo = VDevLo(self)
        self.devices.append(self.lo)
    
    def _init_synchronizer(self):
        self.synchronizer = VDevSynchronizer(self)
    
    def _initialize(self):
        self._init_sandbox()
        self._init_synchronizer()
        self._init_dev()
    
    def __init__(self):
        self.uid = DEFAULT_UID
        self._active = False
        self._initialize()
    
    def _start(self):
        for device in self.devices:
            device.start()
    
    def start(self):
        if not self._active:
            Thread(target=self._start).start()
            self._active = True
