# attr.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
from vdtools.lib.fields import FIELDS
from vdtools.lib.util import get_var_path, mkdir

class Data(object):
    def _get_path(self, uid, name, field):
        path = get_var_path(uid)
        return str(os.path.join(path, field, name))
    
    def initialize(self, uid, name):
        for i in FIELDS:
            path = self._get_path(uid, name, FIELDS[i])
            mkdir(path)
