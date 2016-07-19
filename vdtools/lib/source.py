#      source.py
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
            if func_list[i].startswith('def %s' % func_names[j]):
                res.update({func_names[j]:func_list[i]})
                del func_names[j]
                match = True
                break
        
        if not match:
            raise Exception('Error: failed to get source')
    
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
