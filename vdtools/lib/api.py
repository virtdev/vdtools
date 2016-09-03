# api.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import xattr
from operations import *
from util import get_cmd, readlink

def check_path(func):
    def _check_path(*args, **kwargs):
        path = readlink(args[0])
        return func(path, **kwargs)
    return _check_path

@check_path
def api_touch(path):
    os.system('touch %s' % path)

@check_path
def api_enable(path):
    xattr.setxattr(path, OP_ENABLE, '')

@check_path
def api_disable(path):
    xattr.setxattr(path, OP_DISABLE, '')

@check_path
def api_combine(path, **attr):
    return xattr.getxattr(path, get_cmd(OP_COMBINE, attr))

@check_path
def api_create(path, **attr):
    return xattr.getxattr(path, get_cmd(OP_CREATE, attr))

@check_path
def api_clone(path, **attr):
    return xattr.getxattr(path, get_cmd(OP_CLONE, attr))
