# parser.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
from StringIO import StringIO
from vdtools.lib.ddl import DDL
from vdtools.lib.source import get_func, get_val

VAL_MEMBERS = ['member', 'parent', 'timeout']
FUNC_MEMBERS = ['handler.py', 'filter.py', 'dispatcher.py']
MEMBERS = VAL_MEMBERS + FUNC_MEMBERS

def parse_files(files):
    f = files.get('graph')
    if not f:
        raise Exception('Error: failed to parse, no graph')

    vertex, edge = DDL().parse(f)
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
            files.update({name:open(path)})
    try:
        return parse_files(files)
    finally:
        graph.close()
        for i in files:
            files[i].close()
