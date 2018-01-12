# ddl.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

from vdtools.lib.log import log_err

PTR = '->'
IMAGE = '@'
DEREF = '*'
LBRACE = '['
RBRACE = ']'

SEP_DEV = ','
SEP_NAME = '_'

LEN_PTR = len(PTR)
LEN_DEREF = len(DEREF)

def is_identity(v):
    return v.startswith(DEREF)

def get_identity(v):
    if is_identity(v):
        return v[LEN_DEREF:]

def is_image(v):
    return v.startswith(IMAGE)

def get_image(v):
    if is_image(v):
        buf = v.split(SEP_NAME)
        if len(buf) >= 2:
            return buf[0] + SEP_NAME + buf[1]
        elif buf:
            return buf[0]

def get_type(v):
    buf = v.split(SEP_NAME)
    if buf:
        return buf[0]

class DDL(object):
    def _get_grp(self, buf):
        try:
            grp = []
            cnt = 0
            start = 0
            length = len(buf)
            for i in range(length):
                if buf[i] == LBRACE:
                    cnt += 1
                elif buf[i] == RBRACE:
                    cnt -= 1
                if (buf[i] == SEP_DEV or i == length - 1) and cnt == 0:
                    if i != length - 1:
                        item = buf[start:i]
                        start = i + 1
                    else:
                        item = buf[start:]
                    grp.append(item.strip())
            for i in range(len(grp)):
                item = grp[i]
                if item.startswith(LBRACE):
                    if item.endswith(RBRACE):
                        g = self._get_grp(item[1:-1])
                        if not g:
                            return
                        grp[i] = g
                    else:
                        return
                elif item.find(PTR) >= 0:
                    v = self._get_vertex(item)
                    if not v:
                        return
                    grp[i] = v
            return grp
        except:
            log_err(self, 'failed to get group')
            pass

    def _get_vertex(self, buf):
        try:
            v = ()
            cnt = 0
            start = 0
            items = []
            length = len(buf)
            for i in range(length):
                if buf[i] == LBRACE:
                    cnt += 1
                elif buf[i] == RBRACE:
                    cnt -= 1
                if (buf[i:i + LEN_PTR] == PTR or i == length - 1) and cnt == 0:
                    if i != length - 1:
                        item = buf[start:i]
                        start = i + LEN_PTR
                    else:
                        item = buf[start:]
                    items.append(item.strip())
            for i in range(len(items)):
                item = items[i]
                if item.startswith(LBRACE):
                    if item.endswith(RBRACE):
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

    def _load_graph(self, graph_file):
        graph = ()
        while True:
            line = graph_file.readline()
            if not line:
                break
            ret = self._get_vertex(line.strip())
            if not ret:
                log_err(self, 'failed to load graph')
                return
            graph += (ret,)
        return graph

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
                    if not tmp_start or not tmp_end:
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
                        for j in tmp_start:
                            if type(j) != str:
                                log_err(self, 'invalid graph')
                                return
                            for k in v:
                                if not edges.has_key(k):
                                    edges.update({k:[j]})
                                else:
                                    if j not in edges[k]:
                                        edges[k].append(j)

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

    def parse(self, graph_file):
        try:
            graph = self._load_graph(graph_file)
            vertex = self._check_vertex(graph)
            edge = self._check_edge(graph)
            return (vertex, edge)
        except:
            log_err(self, 'failed to parse')
            return (None, None)
