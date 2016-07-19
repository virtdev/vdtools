#      installer.py
#      
#      Copyright (C) 2016 Yi-Wei Ci <ciyiwei@hotmail.com>
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

import json
from vdtools.lib.util import set_attr
from vdtools.parser import parse_string
from vdtools import combine, create, clone, link
from vdtools.lib.attributes import ATTR_FILTER, ATTR_HANDLER, ATTR_DISPATCHER
from vdtools.lib.dgl import get_type, get_identity, get_image, is_identity, is_image

VDEV = 'VDev'
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
            _install(image, member, parent, timeout, devices)
            pid = devices.get(image)
            if not pid:
                raise Exception('Error: failed to install')
        identity = clone(pid, uid=uid)
        devices.update({name:identity})
        return identity
        
    members = None
    typ = get_type(name)
    if not typ:
        raise Exception('Error: failed to install, invalid graph')
        
    if typ == VDEV:
        if child:
            raise Exception('Error: failed to install, invalid graph')
        members = member.get(name)
        if members and type(members) != list:
            raise Exception('Error: failed to install, invalid graph')
        
    if not members:
        identity = create(typ, uid=uid, parent=parent.get(name))
    else:
        vrtx = []
        for j in members:
            identity = _install(j, member, parent, timeout, devices, child=True)
            if not identity:
                raise Exception('Error: failed to install, invalid identity')
            vrtx.append(identity)
        t = timeout.get(name)
        if not t or type(t) not in (int, float):
            t = TIMEOUT
        identity = combine(vrtx, t, uid=uid)
        if not identity:
            raise Exception('Error: failed to install, cannot combine')
    devices.update({name:identity})
    return identity
    
def install(uid, args):
    res = parse_string(args)
    if not res:
        return
    
    devices = {}
    filt = res.get('filter')
    graph = res.get('graph')
    member = res.get('member')
    parent = res.get('parent')
    handler = res.get('handler')
    timeout = res.get('timeout')
    dispatcher = res.get('dispatcher')
    
    edge = graph['edge']
    vertex = graph['vertex']
    
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
    
    for i in vertex:
        _install(uid, i, member, parent, timeout, devices)
            
    return json.dumps(devices)
