# edge.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
from vdtools.lib.fields import EDGE
from vdtools.lib.util import get_var_path

class Edge(object):
    def _get_path(self, uid, edge, hidden):
        path = get_var_path(uid)
        if not hidden:
            return str(os.path.join(path, EDGE, edge[0], edge[1]))
        else:
            return str(os.path.join(path, EDGE, edge[0], '.' + edge[1]))
    
    def initialize(self, uid, edge, hidden=False):
        path = self._get_path(uid, edge, hidden)
        if not os.path.exists(path):
            with open(path, 'w') as _:
                pass
