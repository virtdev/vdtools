#      source.py
#      
#      Copyright (C) 2015 Yi-Wei Ci <ciyiwei@hotmail.com>
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
import ast
import imp
import string
from lib.log import log_err
from inspect import getsourcelines

class VDSource(object):
    def _get_func(self, path, name):
        mod_name = os.path.basename(path).split('.')[0]
        mod = imp.load_source(mod_name, path)
        func = getattr(mod, name)
        lines = getsourcelines(func)[0]
        lines[0] = string.replace(lines[0], 'def %s' % name, 'def func')
        return ''.join(lines)
        
    def parse(self, path):
        if not os.path.exists(path):
            return
        with open(path) as f:
            buf = f.read()
        module = ast.parse(buf)
        func_list = [item.name for item in module.body if isinstance(item, ast.FunctionDef)]
        if not func_list:
            return
        ret = {}
        for name in func_list:
            src = self._get_func(path, name)
            if not src:
                log_err(self, 'invalid function %s' % name)
                return
            ret.update({name:src})
        return ret
