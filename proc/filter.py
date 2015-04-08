#      filter.py
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

import sandbox
from lib.log import log_err
from loader import VDevLoader
from base64 import encodestring
from sandbox import SANDBOX_PUT
from conf.virtdev import FILTER_PORT

class VDevFilter(object):
    def __init__(self, uid):
        self._filters = {}
        self._loader = VDevLoader(uid)
    
    def _get_code(self, name):
        buf = self._filters.get(name)
        if not buf:
            buf = self._loader.get_filter(name)
            self._filters.update({name:buf})
        return buf
    
    def check(self, name):
        if self._filters.has_key(name):
            if self._filters[name]:
                return True
        else:
            buf = self._loader.get_filter(name)
            self._filters.update({name:buf})
            if buf:
                return True
    
    def remove(self, name):
        if not self._filters.has_key(name):
            return
        del self._filters[name]
    
    def put(self, name, buf):
        try:
            code = self._get_code(name)
            if code:
                return sandbox.request(FILTER_PORT, SANDBOX_PUT, code=encodestring(code), args=buf)
        except:
            log_err(self, 'failed to put')
    