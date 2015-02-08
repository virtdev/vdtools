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
from path import VDEV_FS_LABELS
from lib.log import log_err, log_get
from conf.virtdev import VDEV_FS_PATH, VDEV_FS_MOUNTPOINT, VDEV_DEFAULT_UID

VDEV_ATTR_MODE = 'mode'
VDEV_ATTR_FREQ = 'freq'
VDEV_ATTR_MAPPER = 'mapper'
VDEV_ATTR_HANDLER = 'handler'
VDEV_ATTR_PROFILE = 'profile'
VDEV_ATTR_DISPATCHER = 'dispatcher'
VDEV_ATTR = [VDEV_ATTR_MODE, VDEV_ATTR_FREQ, VDEV_ATTR_MAPPER, VDEV_ATTR_HANDLER, VDEV_ATTR_PROFILE, VDEV_ATTR_DISPATCHER]

def set_attr(uid, name, attr):
    if attr.keys()[0] not in VDEV_ATTR:
        return
    if uid == VDEV_DEFAULT_UID: 
        Attr().initialize(uid, name, attr)

def get_attr(uid, name, attr):
    ret = ''
    if attr not in VDEV_ATTR:
        return ret
    path = os.path.join(VDEV_FS_MOUNTPOINT, uid, VDEV_FS_LABELS['attr'], name, attr)
    if os.path.exists(path):
        with open(path) as f:
            ret = f.read()
    return ret

class Attr(object):
    def _get_path(self, uid, name):
        return str(os.path.join(VDEV_FS_PATH, uid, 'attr', name))
    
    def create(self, uid, name):
        path = self._get_path(uid, name)
        return os.open(path, os.O_RDWR | os.O_CREAT, 0644)
    
    def _release(self, uid, name, fh, force=False):
        os.close(fh)
    
    def _create_mapper(self, uid, name, val):
        name = os.path.join(name, VDEV_ATTR_MAPPER)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_mode(self, uid, name, val):
        name = os.path.join(name, VDEV_ATTR_MODE)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_freq(self, uid, name, val):
        name = os.path.join(name, VDEV_ATTR_FREQ)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_handler(self, uid, name, val):
        name = os.path.join(name, VDEV_ATTR_HANDLER)
        f = self.create(uid, name)
        try:
            os.write(f, str(val))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_profile(self, uid, name, val):
        name = os.path.join(name, VDEV_ATTR_PROFILE)
        f = self.create(uid, name)
        try:
            for i in val:
                os.write(f, '%s=%s\n' % (str(i), str(val[i])))
        finally:
            self._release(uid, name, f, force=True)
    
    def _create_dispatcher(self, uid, name, val):
        name = os.path.join(name, VDEV_ATTR_DISPATCHER)
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
        if key == VDEV_ATTR_MAPPER:
            self._create_mapper(uid, name, val)
        elif key == VDEV_ATTR_MODE:
            self._create_mode(uid, name, val)
        elif key == VDEV_ATTR_FREQ:
            self._create_freq(uid, name, val)
        elif key == VDEV_ATTR_HANDLER:
            self._create_handler(uid, name, val)
        elif key == VDEV_ATTR_PROFILE:
            self._create_profile(uid, name, val)
        elif key == VDEV_ATTR_DISPATCHER:
            self._create_dispatcher(uid, name, val)
    