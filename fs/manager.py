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

from fs.path import load
from dev.lo import VDevLo
from threading import Thread
from proc.sandbox import VDevSandbox
from dev.vdev import VDev, VDEV_MODE_VIRT
from proc.synchronizer import VDevSynchronizer
from conf.virtdev import VDEV_MAPPER_PORT, VDEV_HANDLER_PORT, VDEV_DISPATCHER_PORT, VDEV_DEFAULT_UID

def excl(func):
    def _excl(*args, **kwargs):
        self = args[0]
        self._lock.acquire()
        try:
            return func(*args, **kwargs)
        finally:
            self._lock.release()
    return _excl

def excl_name(func):
    def _excl_name(*args, **kwargs):
        self = args[0]
        name = args[1]
        lock = self._lock.acquire(name)
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()
    return _excl_name


class VDevFSManager(object):
    def _init_sandbox(self):
        self._mapper = VDevSandbox(VDEV_MAPPER_PORT)
        self._handler = VDevSandbox(VDEV_HANDLER_PORT)
        self._dispatcher = VDevSandbox(VDEV_DISPATCHER_PORT)
        self._mapper.start()
        self._handler.start()
        self._dispatcher.start()
    
    def _prepare(self):
        self.devices = []
        self._mapper = None
        self._handler = None
        self._dispatcher = None
        self.lo = VDevLo(self)
        self._init_sandbox()
        self.devices.append(self.lo)
        self.synchronizer = VDevSynchronizer(self)
        
    def __init__(self):
        self.uid = VDEV_DEFAULT_UID
        self._active = False
        self._prepare()
    
    def _start(self):
        names = load(self.uid, sort=True)
        if names:
            for n in names:
                mode = self.synchronizer.get_mode(n)
                if mode & VDEV_MODE_VIRT:
                    device = VDev(mode)
                    device.mount(self, n)
        for device in self.devices:
            device.start()
    
    def start(self):
        if not self._active:
            Thread(target=self._start).start()
            self._active = True