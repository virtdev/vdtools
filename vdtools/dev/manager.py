# manager.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

from threading import Thread
from vdtools.conf.user import UID
from vdtools.proc.core import Core
from vdtools.proc.proc import Proc
from vdtools.dev.interface.lo import Lo
from vdtools.conf.defaults import PROC_ADDR, FILTER_PORT, HANDLER_PORT, DISPATCHER_PORT

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
        self.uid = UID
        self.channel = None
        self._active = False
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
