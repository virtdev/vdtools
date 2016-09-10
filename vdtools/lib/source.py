# source.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import ast

def get_func(source_file):
    res = {}
    buf = source_file.read()
    module = ast.parse(buf)
    func_names = [item.name for item in module.body if isinstance(item, ast.FunctionDef)]
    if not func_names:
        return res
    
    func_list = buf.split('\ndef')
    for i in range(len(func_list)):
        if not func_list[i].startswith('def'):
            func_list[i] = 'def' + func_list[i]
        
        match = False
        total = len(func_names)
        for j in range(total):
            head = 'def %s' % func_names[j]
            if func_list[i].startswith(head):
                body = 'def func' + func_list[i][len(head):]
                res.update({func_names[j]:body})
                del func_names[j]
                match = True
                break
        
        if not match:
            raise Exception('Error: failed to get function')
    
    return res

def get_val(source_file):
    res = {}
    buf = source_file.readlines()
    for item in buf:
        key, val = item.split('=')
        k = key.strip()
        v = val.strip()
        if v.startswith('[') and v.endswith(']'):
            v = v[1:len(v) - 1].split(',')
        res.update({k:v})
    return res
