#      attr.py
#      
#      Copyright (C) 2016 Yi-Wei Ci <ciyiwei@hotmail.com>
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

import os
import json
from vdtools.lib.fields import ATTR
from vdtools.conf.env import PATH_VAR
from vdtools.lib.log import log_err, log_get
from vdtools.lib.attributes import ATTRIBUTES, ATTR_PROFILE

class Attr(object):
    def _get_path(self, uid, name):
        return str(os.path.join(PATH_VAR, uid, ATTR, name))
    
    def create(self, uid, name):
        path = self._get_path(uid, name)
        return os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    
    def _release(self, uid, name, fh, force=False):
        os.close(fh)
    
    def _init_attr(self, uid, name, attr, val):
        name = os.path.join(name, attr)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def initialize(self, uid, name, attr, val):
        if attr not in ATTRIBUTES:
            log_err(self, 'invalid attribute %s' % str(attr))
            raise Exception(log_get(self, 'invalid attribute'))
        if attr == ATTR_PROFILE:
            val = json.dumps(val)
        self._init_attr(uid, name, attr, val)
