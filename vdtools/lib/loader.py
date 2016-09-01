# loader.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
import json
from vdtools.lib.fields import ATTR
from vdtools.lib.attributes import ATTR_PROFILE
from vdtools.lib.util import unicode2str, get_mnt_path

class Loader(object):
    def __init__(self, uid):
        self._uid = uid
    
    def _get_path(self, name, attr):
        path = get_mnt_path(self._uid)
        return os.path.join(path, ATTR, name, attr)
    
    def _read(self, name, attr):
        path = self._get_path(name, attr)
        print 'loader: read, path=%s' % path
        try:
            os.stat(path)
        except:
            return ''
        with open(path, 'r') as f:
            buf = f.read()
        return buf
    
    def get_attr(self, name, attr, typ):
        buf = self._read(name, attr)
        if buf:
            return typ(buf)
    
    def get_profile(self, name):
        buf = self._read(name, ATTR_PROFILE)
        if buf:
            attr = json.loads(buf)
            return unicode2str(attr)
