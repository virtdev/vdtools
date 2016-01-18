#      attribute.py
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

import os
import json
from lib.attributes import *
from conf.virtdev import PATH_FS
from lib.domains import ATTRIBUTE
from lib.log import log_err, log_get
from lib.util import unicode2str, DEFAULT_UID

def set_attr(uid, name, attr, val):
    if attr not in ATTRIBUTES:
        return
    if uid == DEFAULT_UID:
        Attribute().initialize(uid, name, attr, val)

def get_attr(uid, name, attr):
    ret = ''
    if attr not in ATTRIBUTES:
        return ret
    path = os.path.join(PATH_FS, uid, ATTRIBUTE, name, attr)
    if os.path.exists(path):
        with open(path) as f:
            ret = f.read()
    return ret

class Attribute(object):
    def _get_path(self, uid, name):
        return str(os.path.join(PATH_FS, uid, 'attr', name))
    
    def create(self, uid, name):
        path = self._get_path(uid, name)
        return os.open(path, os.O_RDWR | os.O_CREAT, 0644)
    
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
            raise Exception(log_get(self,' invalid attribute'))
        if attr == ATTR_PROFILE:
            val = json.dumps(val)
        self._init_attr(uid, name, attr, val)

    def get_profile(self, uid, name):
        name = os.path.join(name, ATTR_PROFILE)
        path = self._get_path(uid, name)
        fd = os.open(path, os.O_RDONLY)
        if not fd:
            log_err(self, 'failed to get profile')
            raise Exception(log_get(self, 'failed to get profile'))
        try:
            st = os.fstat(fd)
            buf = os.read(fd, st.st_size)
            if buf:
                attr = json.loads(buf)
                return unicode2str(attr) 
        finally:
            os.close(fd)
