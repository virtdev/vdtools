#      parser.py
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

import os
from StringIO import StringIO
from vdtools.lib.dgl import DGL
from vdtools.lib.source import get_func, get_val

VAL_MEMBERS = ['member', 'parent', 'timeout']
FUNC_MEMBERS = ['handler.py', 'filter.py', 'dispatcher.py']
MEMBERS = VAL_MEMBERS + FUNC_MEMBERS

def parse_files(files):
    f = files.get('graph')
    if not f:
        raise Exception('Error: failed to parse, no graph')
    
    vertex, edge = DGL().parse(f)
    if not vertex or not edge:
        raise Exception('Error: failed to parse, invalid graph')
    
    res = {'graph':{'vertex':vertex, 'edge':edge}}
    for i in VAL_MEMBERS:
        content = {}
        f = files.get(i)
        if f:
            content = get_val(f)
        res.update({i:content})
    
    for i in FUNC_MEMBERS:
        content = {}
        f = files.get(i)
        if f:
            content = get_func(f)
        res.update({i:content})
    
    return res

def parse_string(args):
    graph = args.get('graph')
    if not graph:
        raise Exception('Error: failed to parse, no graph')
    files = {'graph':StringIO(graph)}
    for i in args:
        if i in MEMBERS:
            files.update({i:StringIO(args[i])})
    return parse_files(files)

def parse(proj_dir):
    files = {}
    path = os.path.join(proj_dir, 'graph')
    if not os.path.exists(path):
        raise Exception('Error: failed to parse, no graph')
    graph = open(path)
    files.update({'graph':graph})
    
    for name in MEMBERS:
        path = os.path.join(proj_dir, name)
        if os.path.exists(path):
            f = open(path)
            files.update({name:f})
    try:
        return parse_files(files)
    finally:
        graph.close()
        for i in files:
            files[i].close()
