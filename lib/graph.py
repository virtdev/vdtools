#      graph.py
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

from lib.log import log_err

VDG_PTR = '->'
VDG_PTR_LEN = len(VDG_PTR)

class VDGraph(object):
    def _get_grp(self, buf):
        try:
            grp = []
            cnt = 0
            start = 0
            length = len(buf)
            for i in range(length):
                if buf[i] == '[':
                    cnt += 1
                elif buf[i] == ']':
                    cnt -= 1
                if (buf[i] == ',' or i == length - 1) and cnt == 0:
                    if i != length - 1:
                        item = buf[start:i]
                        start = i + 1
                    else:
                        item = buf[start:]
                    grp.append(item.strip())
            for i in range(len(grp)):
                item = grp[i]
                if item.startswith('['):
                    if item.endswith(']'):
                        g = self._get_grp(item[1:-1])
                        if not g:
                            return
                        grp[i] = g
                    else:
                        return
                elif item.find(VDG_PTR) >= 0:
                    v = self._get_vertex(item)
                    if not v:
                        return
                    grp[i] = v
            return grp
        except:
            log_err(self, 'failed to get grp')
            pass
    
    def _get_vertex(self, buf):
        try:
            v = ()
            cnt = 0
            start = 0
            items = []
            length = len(buf)
            for i in range(length):
                if buf[i] == '[':
                    cnt += 1
                elif buf[i] == ']':
                    cnt -= 1
                if (buf[i:i + VDG_PTR_LEN] == VDG_PTR or i == length - 1) and cnt == 0:
                    if i != length - 1:
                        item = buf[start:i]
                        start = i + VDG_PTR_LEN
                    else:
                        item = buf[start:]
                    items.append(item.strip())
            for i in range(len(items)):
                item = items[i]
                if item.startswith('['):
                    if item.endswith(']'):
                        grp = self._get_grp(item[1:-1])
                        if not grp:
                            return
                        v += (grp,)
                    else:
                        return
                else:
                    v += (item,)
            return v
        except:
            log_err(self, 'failed to get vertex')
            pass
    
    def _load_graph(self, path):
        g = ()
        with open(path) as f:
            while True:
                l = f.readline()
                if not l:
                    break
                ret = self._get_vertex(l.strip())
                if not ret:
                    log_err(self, 'failed to parse')
                    return
                g += (ret,)
        return g
                
    def _check_vertex(self, graph):
        v = []
        for item in graph:
            if type(item) == str:
                if item not in v:
                    v.append(item)
            else:
                ret = self._check_vertex(item) 
                for i in ret:
                    if i not in v:
                        v.append(i)
        return v
    
    
    def _extract_edges(self, graph):
        end = []
        start = []
        edges = {}
        if type(graph) == tuple:
            v = graph[0]
            length = len(graph)
            if type(v) != str:
                edges, start, tmp_end = self._extract_edges(v)
                if length == 1:
                    end = tmp_end
                else:
                    v = tmp_end
            else:
                start.append(v)
                if length == 1:
                    log_err(self, 'invalid graph')
                    return
            for cnt in range(1, length):
                i = graph[cnt]
                if type(i) == str:
                    if type(v) == str:
                        if not edges.has_key(v):
                            edges.update({v:[i]})
                        elif i not in edges[v]:
                            edges[v].append(i)
                    else:
                        for j in v:
                            if type(j) != str:
                                log_err(self, 'invalid graph')
                                return
                            if not edges.has_key(j):
                                edges.update({j:[i]})
                            elif i not in edges[j]:
                                edges[j].append(i)
                    if cnt == length - 1:
                        end.append(i)
                    else:
                        v = i
                else:
                    tmp_edges, tmp_start, tmp_end = self._extract_edges(i)
                    if not tmp_start or not tmp_end or (type(v) != str and len(v) > 1 and len(tmp_start) > 1):
                        log_err(self, 'invalid graph')
                        return
                    if type(v) == str or len(v) == 1:
                        if type(v) != str:
                            if type(v[0]) != str:
                                log_err(self, 'invalid graph')
                                return
                            v = v[0]
                        if not edges.has_key(v):
                            edges.update({v:tmp_start})
                        else:
                            for j in tmp_start:
                                if j not in edges[v]:
                                    edges[v].append(j)
                    else:
                        tmp = tmp_start[0]
                        if type(tmp) != str:
                            log_err(self, 'invalid graph')
                            return
                        for j in v:
                            if not edges.has_key(j):
                                edges.update({j:tmp})
                            else:
                                if tmp not in edges[j]:
                                    edges[j].append(tmp)
                    
                    for j in tmp_edges:
                        if type(j) != str:
                            log_err(self, 'invalid graph')
                            return
                        if not edges.has_key(j):
                            edges.update({j:tmp_edges[j]})
                        else:
                            for k in tmp_edges[j]:
                                if k not in edges[j]:
                                    edges[j].append(k)
                    
                    if cnt == length - 1:
                        end = tmp_end
                    else:
                        v = tmp_end
        elif type(graph) == list:
            for i in graph:
                if type(i) == str:
                    start.append(i)
                    end.append(i)
                else:
                    tmp_edges, tmp_start, tmp_end = self._extract_edges(i)
                    for j in tmp_start:
                        if j not in start:
                            start.append(j)
                    for j in tmp_end:
                        if j not in end:
                            end.append(j)
                    for j in tmp_edges:
                        if type(j) != str:
                            log_err(self, 'invalid graph')
                            return
                        if not edges.has_key(j):
                            edges.update({j:tmp_edges[j]})
                        else:
                            for k in tmp_edges[j]:
                                if k not in edges[j]:
                                    edges[j].append(k)
        else:
            log_err(self, 'invalid graph')
        return (edges, start, end)
            
    def _check_edge(self, graph):
        e = {}
        for i in graph:
            edges, _, _ = self._extract_edges(i)
            for j in edges:
                if e.has_key(j):
                    for k in edges[j]:
                        if k not in e[j]:
                            e[j].append(k)
                else:
                    e.update({j:edges[j]})
        return e
    
    def parse(self, path):
        try:
            g = self._load_graph(path)
            v = self._check_vertex(g)
            e = self._check_edge(g)
            return (v, e)
        except:
            log_err(self, 'failed to parse')
            return (None, None)
    
    def is_virtual_vertex(self, v):
        if not v.startswith('@'):
            return True
    
    def get_vertex_type(self, v):
        if v.startswith('@'):
            typ = v[1:]
            pair = typ.split('_')
            length = len(pair)
            if length == 2:
                return pair[0]
            elif length == 1:
                return typ
    