# vrtx.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
from vdtools.lib.fields import VRTX
from vdtools.lib.util import get_var_path

class Vrtx(object):
    def _get_path(self, uid, name, vrtx):
        path = get_var_path(uid)
        return str(os.path.join(path, VRTX, name, vrtx))
    
    def initialize(self, uid, name, vrtx):
        for i in vrtx:
            path = self._get_path(uid, name, i)
            if not os.path.exists(path):
                with open(path, 'w') as _:
                    pass
