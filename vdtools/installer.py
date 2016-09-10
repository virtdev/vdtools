# installer.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import json
from vdtools.conf.user import UID
from vdtools.lib.types import VDEV
from vdtools.lib.util import set_attr
from vdtools.parser import parse_string
from vdtools import combine, create, clone, link
from vdtools.lib.attributes import ATTR_FILTER, ATTR_HANDLER, ATTR_DISPATCHER
from vdtools.lib.ddl import get_type, get_identity, get_image, is_identity, is_image

TIMEOUT = 5 # seconds

def _install(uid, name, member, parent, timeout, devices, child=False):
    if name in devices:
        return devices[name]
    
    if is_identity(name):
        identity = get_identity(name)
        devices.update({name:identity})
        return identity
    elif is_image(name):
        image = get_image(name)
        if get_type(image) == VDEV:
            raise Exception('Error: failed to install, invalid type')
        pid = devices.get(image)
        if not pid:
            _install(uid, image, member, parent, timeout, devices)
            pid = devices.get(image)
            if not pid:
                raise Exception('Error: failed to install')
        identity = clone(pid, uid=uid)
        devices.update({name:identity})
        return identity
    
    typ = get_type(name)
    if not typ:
        raise Exception('Error: failed to install, invalid graph')
    
    members = member.get(name)
    if members and type(members) != list:
        raise Exception('Error: failed to install, invalid graph')
    
    if not members:
        identity = create(typ, parent=parent.get(name), uid=uid)
    else:
        vrtx = []
        for j in members:
            identity = _install(uid, j, member, parent, timeout, devices, child=True)
            if not identity:
                raise Exception('Error: failed to install, invalid identity')
            vrtx.append(identity)
        t = timeout.get(name)
        if t and type(t) in (int, float):
            t = TIMEOUT
        identity = combine(typ, vrtx, t, uid=uid)
        if not identity:
            raise Exception('Error: failed to install, cannot combine')
    
    devices.update({name:identity})
    return identity

def install(uid, args):
    if not uid:
        uid = UID
    
    res = parse_string(args)
    if not res:
        return
    
    graph = res.get('graph')
    member = res.get('member')
    parent = res.get('parent')
    timeout = res.get('timeout')
    
    filt = res.get('filter.py')
    handler = res.get('handler.py')
    dispatcher = res.get('dispatcher.py')
    
    edge = graph['edge']
    vertex = graph['vertex']
    
    devices = {}
    for i in vertex:
        _install(uid, i, member, parent, timeout, devices)
    
    if handler:
        for i in handler:
            if i in devices and not is_image(i) and not is_identity(i):
                set_attr(uid, devices[i], ATTR_HANDLER, handler[i])
    
    if filt:
        for i in filt:
            if i in devices and not is_image(i) and not is_identity(i):
                set_attr(uid, devices[i], ATTR_FILTER, filt[i])
    
    if dispatcher:
        for i in dispatcher:
            if i in devices and not is_image(i) and not is_identity(i):
                set_attr(uid, devices[i], ATTR_DISPATCHER, dispatcher[i])
    
    for i in edge:
        for j in edge[i]:
            if j != i:
                if not devices.has_key(i) or not devices.has_key(j):
                    raise Exception('Error: failed to install, invalid graph')
                link(devices[i], devices[j], uid=uid)
    
    return json.dumps(devices)
