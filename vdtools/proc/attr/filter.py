# filter.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

from vdtools.proc import proc
from vdtools.lib.log import log_err
from vdtools.lib.loader import Loader
from vdtools.lib.attributes import ATTR_FILTER
from vdtools.conf.defaults import PROC_ADDR, FILTER_PORT

class Filter(object):
    def __init__(self, uid, addr=PROC_ADDR):
        self._addr = addr
        self._filters = {}
        self._loader = Loader(uid)

    def _get_code(self, name):
        buf = self._filters.get(name)
        if not buf:
            buf = self._loader.get_attr(name, ATTR_FILTER, str)
            self._filters.update({name:buf})
        return buf

    def check(self, name):
        if self._filters.get(name):
            return True
        else:
            buf = self._loader.get_attr(name, ATTR_FILTER, str)
            if buf:
                self._filters.update({name:buf})
                return True

    def remove(self, name):
        if self._filters.has_key(name):
            del self._filters[name]

    def put(self, name, buf):
        try:
            code = self._get_code(name)
            if code == None:
                code = self._get_code(name)
                if not code:
                    return
            return proc.put(self._addr, FILTER_PORT, code, buf)
        except:
            log_err(self, 'failed to put')
