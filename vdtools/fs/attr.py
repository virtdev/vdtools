# attr.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
import json
from vdtools.lib.fields import ATTR
from vdtools.lib.util import get_var_path
from vdtools.lib.log import log_err, log_get
from vdtools.lib.attributes import ATTRIBUTES, ATTR_PROFILE

class Attr(object):
    def _get_path(self, uid, name):
        path = get_var_path(uid)
        return str(os.path.join(path, ATTR, name))
    
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
