#      attr.py
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
from path import DOMAIN
from lib.log import log_err, log_get
from conf.virtdev import FS_PATH, MOUNTPOINT, DEFAULT_UID

ATTR_MODE = 'mode'
ATTR_FREQ = 'freq'
ATTR_FILTER = 'filter'
ATTR_HANDLER = 'handler'
ATTR_PROFILE = 'profile'
ATTR_DISPATCHER = 'dispatcher'
ATTRIBUTES = [ATTR_MODE, ATTR_FREQ, ATTR_FILTER, ATTR_HANDLER, ATTR_PROFILE, ATTR_DISPATCHER]

def set_attr(uid, name, attr):
    if attr.keys()[0] not in ATTRIBUTES:
        return
    if uid == DEFAULT_UID: 
        Attr().initialize(uid, name, attr)

def get_attr(uid, name, attr):
    ret = ''
    if attr not in ATTRIBUTES:
        return ret
    path = os.path.join(MOUNTPOINT, uid, DOMAIN['attr'], name, attr)
    if os.path.exists(path):
        with open(path) as f:
            ret = f.read()
    return ret

class Attr(object):
    def _get_path(self, uid, name):
        return str(os.path.join(FS_PATH, uid, 'attr', name))
    
    def create(self, uid, name):
        path = self._get_path(uid, name)
        return os.open(path, os.O_RDWR | os.O_CREAT, 0644)
    
    def _release(self, uid, name, fh, force=False):
        os.close(fh)
    
    def _create_filter(self, uid, name, val):
        name = os.path.join(name, ATTR_FILTER)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_mode(self, uid, name, val):
        name = os.path.join(name, ATTR_MODE)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_freq(self, uid, name, val):
        name = os.path.join(name, ATTR_FREQ)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_handler(self, uid, name, val):
        name = os.path.join(name, ATTR_HANDLER)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_profile(self, uid, name, val):
        name = os.path.join(name, ATTR_PROFILE)
        f = self.create(uid, name)
        try:
            for i in val:
                os.write(f, '%s=%s\n' % (str(i), str(val[i])))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_dispatcher(self, uid, name, val):
        name = os.path.join(name, ATTR_DISPATCHER)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def initialize(self, uid, name, attr):
        if type(attr) != dict or len(attr) != 1:
            log_err(self, 'failed to initialize, invalid attr')
            raise Exception(log_get(self, 'failed to initialize, invalid attr'))
        key = attr.keys()[0]
        val = attr[key]
        if key == ATTR_FILTER:
            self._create_filter(uid, name, val)
        elif key == ATTR_MODE:
            self._create_mode(uid, name, val)
        elif key == ATTR_FREQ:
            self._create_freq(uid, name, val)
        elif key == ATTR_HANDLER:
            self._create_handler(uid, name, val)
        elif key == ATTR_PROFILE:
            self._create_profile(uid, name, val)
        elif key == ATTR_DISPATCHER:
            self._create_dispatcher(uid, name, val)
    