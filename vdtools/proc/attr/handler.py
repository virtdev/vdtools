# handler.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

from vdtools.proc import proc
from vdtools.lib.log import log_err
from vdtools.lib.loader import Loader
from vdtools.lib.attributes import ATTR_HANDLER
from vdtools.conf.defaults import PROC_ADDR, HANDLER_PORT

class Handler(object):
    def __init__(self, uid, addr=PROC_ADDR):
        self._handlers = {}
        self._loader = Loader(uid)
        self._addr = addr

    def _get_code(self, name):
        buf = self._handlers.get(name)
        if not buf:
            buf = self._loader.get_attr(name, ATTR_HANDLER, str)
            self._handlers.update({name:buf})
        return buf

    def remove(self, name):
        if self._handlers.has_key(name):
            del self._handlers[name]

    def check(self, name):
        if self._handlers.get(name):
            return True
        else:
            buf = self._loader.get_attr(name, ATTR_HANDLER, str)
            if buf:
                self._handlers.update({name:buf})
                return True

    def put(self, name, buf):
        try:
            code = self._get_code(name)
            if code == None:
                code = self._get_code(name)
                if not code:
                    return
            return proc.put(self._addr, HANDLER_PORT, code, buf)
        except:
            log_err(self, 'failed to put')
