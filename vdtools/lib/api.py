# api.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import xattr
from util import get_cmd
from operations import *

def api_touch(path):
    os.system('touch %s' % path)

def api_enable(path):
    xattr.setxattr(path, OP_ENABLE, '')

def api_disable(path):
    xattr.setxattr(path, OP_DISABLE, '')
    
def api_combine(path, **attr):
    return xattr.getxattr(path, get_cmd(OP_COMBINE, attr))

def api_create(path, **attr):
    return xattr.getxattr(path, get_cmd(OP_CREATE, attr))

def api_clone(path, **attr):
    return xattr.getxattr(path, get_cmd(OP_CLONE, attr))
