# core.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import time
from datetime import datetime
from threading import Event, Thread
from vdtools.conf.log import LOG_CORE
from vdtools.lib.lock import NamedLock
from vdtools.proc.attr.freq import Freq
from vdtools.proc.attr.mode import Mode
from vdtools.proc.attr.filter import Filter
from vdtools.proc.attr.parent import Parent
from vdtools.proc.attr.handler import Handler
from vdtools.proc.attr.timeout import Timeout
from vdtools.proc.attr.dispatcher import Dispatcher
from vdtools.lib.fields import FIELD_EDGE, FIELD_VRTX
from vdtools.lib.log import log_debug, log_err, log_get
from vdtools.lib.util import named_lock, get_devices, save_device
from vdtools.lib.operations import OP_GET, OP_PUT, OP_OPEN, OP_CLOSE
from vdtools.lib.modes import MODE_VIRT, MODE_SWITCH, MODE_IN, MODE_OUT, MODE_REFLECT, MODE_CLONE

INSP_INTV = 5 # seconds
LIST_SIZE = 2

class Core(object):
    def __init__(self, manager):
        self._events = {}
        self._members = {}
        self._manager = manager
        self._uid = manager.uid
        self._lock = NamedLock()
        self._mode = Mode(self._uid)
        self._freq = Freq(self._uid)
        self._filter = Filter(self._uid)
        self._parent = Parent(self._uid)
        self._timeout = Timeout(self._uid)
        self._handler = Handler(self._uid)
        self._inspector = Thread(target=self._start_inspector)
        self._dispatcher = Dispatcher(self._uid, manager.channel, self)
        self._inspector.start()
    
    def _log(self, text):
        if LOG_CORE:
            log_debug(self, text)
    
    def _can_put(self, dest, src, flags):
        if flags & MODE_REFLECT:
            return True
        else:
            return not self._members[dest] or self._members[dest].has_key(src)
    
    def _check_paths(self, name):
        if not self._dispatcher.has_edge(name):
            edges = get_devices(self._uid, name, FIELD_EDGE)
            self._dispatcher.update_edges(name, edges)
    
    def _check_members(self, name):
        if not self._members.has_key(name):
            self._members[name] = {}
            members = get_devices(self._uid, name, FIELD_VRTX)
            for i in members:
                self._members[name][i] = []
    
    def _count(self, name):
        cnt = 0
        for i in self._members[name]:
            if len(self._members[name][i]) > 0:
                cnt += 1
        return cnt
    
    def _check_timeout(self, name):
        if not self._members[name]:
            return
        timeout = None
        try:
            timeout = self._timeout.get(name)
        except:
            log_err(self, 'failed to check timeout')
        if not timeout:
            return
        t_min = None
        for i in self._members[name]:
            if len(self._members[name][i]) > 0:
                _, t = self._members[name][i][0]
                if not t_min:
                    t_min = t
                elif t < t_min:
                    t_min = t
        if t_min:
            t = datetime.utcnow()
            if (t - t_min).total_seconds() >= timeout:
                return True
    
    def _inspect(self, name):
        try:
            if self._check_timeout(name):
                args = self._pop_args(name)
                if self._filter.check(name):
                    args = self._filter.put(name, args)
                if args and type(args) == dict:
                    res = self._proc(name, args)
                    if res:
                        self.dispatch(name, res)
        except:
            log_err(self, 'failed to inspect, name=%s' % str(name))
    
    def _start_inspector(self):
        while True:
            time.sleep(INSP_INTV)
            for name in self._members:
                self._inspect(name)
    
    def _is_ready(self, dest, src, flags):
        if flags & MODE_REFLECT or not self._members[dest]:
            return True
        elif self._members[dest].has_key(src) and not len(self._members[dest][src]):
            if self._count(dest) + 1 == len(self._members[dest]):
                return True
    
    def _get_event(self, dest, src):
        if not self._events.has_key(dest):
            self._events[dest] = {}
        if not self._events[dest].has_key(src):
            ev = Event()
            self._events[dest][src] = [ev, 1]
        else:
            ev = self._events[dest][src][0]
            self._events[dest][src][1] += 1
        ev.clear()
        return ev
    
    def _set_event(self, dest, src):
        if self._events.has_key(dest):
            if self._events[dest].has_key(src):
                ev = self._events[dest][src][0]
                ev.set()
    
    def _put_event(self, dest, src):
        if self._events.has_key(dest):
            if self._events[dest].has_key(src):
                cnt = self._events[dest][src][1]
                if cnt == 1:
                    del self._events[dest][src]
                elif cnt > 1:
                    self._events[dest][src][1] -= 1
                else:
                    log_err(self, 'failed to put event, dest=%s, src=%s' % (dest, src))
                    raise Exception(log_get(self, 'failed to put event'))
            if not self._events[dest]:
                del self._events[dest]
    
    @named_lock
    def _remove_edge(self, name, edge):
        self._dispatcher.remove_edge(edge)
    
    def remove_edge(self, edge):
        name = edge[0]
        self._remove_edge(name, edge)
    
    @named_lock
    def remove_handler(self, name):
        self._handler.remove(name)
    
    @named_lock
    def remove_filter(self, name):
        self._filter.remove(name)
    
    @named_lock
    def remove_dispatcher(self, name):
        self._dispatcher.remove(name)
    
    @named_lock
    def remove_mode(self, name):
        self._mode.remove(name)
    
    @named_lock
    def remove_freq(self, name):
        self._freq.remove(name)
    
    @named_lock
    def remove_timeout(self, name):
        self._timeout.remove(name)
    
    @named_lock
    def _add_edge(self, name, edge):
        self._dispatcher.add_edge(edge)
    
    def add_edge(self, edge):
        name = edge[0]
        self._add_edge(name, edge)
    
    def get_mode(self, name):
        return self._mode.get(name)
    
    def get_freq(self, name):
        return self._freq.get(name)
    
    def _remove(self, name):
        if not self._members.has_key(name):
            return
        if self._events.has_key(name):
            for i in self._events[name]:
                self._events[name][i].set()
        del self._members[name]
    
    @named_lock
    def remove(self, name):
        self._dispatcher.remove_edges(name)
        self.remove_dispatcher(name)
        self.remove_handler(name)
        self.remove_filter(name)
        self.remove_timeout(name)
        self.remove_freq(name)
        self.remove_mode(name)
        self._remove(name)
    
    @named_lock
    def dispatch(self, name, buf):
        self._check_paths(name)
        if not self._dispatcher.check(name):
            self._log('dispatch, name=%s' % name)
            self._dispatcher.send(name, buf)
        else:
            blocks = self._dispatcher.put(name, buf)
            if blocks and type(blocks) == list:
                self._log('dispatch blocks, name=%s' % name)
                self._dispatcher.send_blocks(name, blocks)
    
    def get_oper(self, buf, mode):
        if type(buf) != dict:
            return
        if mode & MODE_SWITCH:
            ret = None
            for i in buf:
                if type(buf[i]) == dict and buf[i].has_key('enable'):
                    tmp = buf[i]['Enable'] in ('True', 'true', True)
                    if ret != None:
                        if tmp != ret:
                            return
                    else:
                        ret = tmp
            if ret:
                return OP_OPEN
            else:
                return OP_CLOSE
        elif mode & MODE_IN:
            if 1 == len(buf):
                return OP_PUT
        elif mode & MODE_OUT:
            return OP_GET
    
    def _handle(self, name, buf):
        mode = self._mode.get(name)
        if not mode & MODE_VIRT:
            oper = self.get_oper(buf, mode)
            if not oper:
                return
            for device in self._manager.devices:
                dev = device.find(name)
                if dev:
                    self._log('handle, name=%s, oper=%s, dev=%s' % (name, oper, dev.d_name))
                    return dev.proc(name, oper, buf)
        else:
            return buf
    
    def has_handler(self, name):
        return self._handler.check(name)
    
    def handle(self, name, buf):
        return self._handler.put(name, buf)
    
    def _proc(self, name, buf):
        try:
            if not self.has_handler(name):
                return self._handle(name, buf)
            else:
                return self.handle(name, buf)
        except:
            log_err(self, 'failed to process, name=%s' % name)
    
    def _get_args(self, dest, src, buf, flags):
        try:
            args = {}
            args[src] = buf
            if not flags & MODE_REFLECT:
                for i in self._members[dest]:
                    if i != src and len(self._members[dest][i]) > 0:
                        args[i] = self._members[dest][i][0][0]
                        self._members[dest][i].pop(0)
                        self._set_event(dest, i)
            return args
        except:
            log_err(self, 'failed to get args, dest=%s, src=%s' % (dest, src))
    
    def _pop_args(self, name):
        try:
            args = {}
            for i in self._members[name]:
                if len(self._members[name][i]) > 0:
                    args[i] = self._members[name][i][0][0]
                    self._members[name][i].pop(0)
                    self._set_event(name, i)
            return args
        except:
            log_err(self, 'failed to pop args, name=%s' % name)
    
    def _check_list(self, dest, src):
        while len(self._members[dest][src]) >= LIST_SIZE:
            ev = self._get_event(dest, src)
            self._lock.release(dest)
            try:
                ev.wait()
            finally:
                self._lock.acquire(dest)
            self._put_event(dest, src)
    
    def _try_put(self, dest, src, buf, flags):
        try:
            args = None
            if not self._is_ready(dest, src, flags):
                self._check_list(dest, src)
                self._members[dest][src].append((buf, datetime.utcnow()))
                if self._check_timeout(dest):
                    args = self._pop_args(dest)
            else:
                args = self._get_args(dest, src, buf, flags)
            if args:
                if self._filter.check(dest):
                    args = self._filter.put(dest, args)
                if args and type(args) == dict:
                    return self._proc(dest, args)
        except:
            log_err(self, 'failed to put, dest=%s, src=%s' % (dest, src))
    
    def put(self, dest, src, buf, flags):
        if not buf:
            self._log('put, no content, dest=%s, src=%s' % (dest, src))
            return
        res = None
        mode = self._mode.get(dest)
        if not mode & MODE_CLONE:
            if not flags & MODE_REFLECT:
                self._check_members(dest)
            if self._can_put(dest, src, flags):
                res = self._try_put(dest, src, buf, flags)
        else:
            if not flags & MODE_REFLECT:
                flags |= MODE_REFLECT
                src = self._parent.get(dest)
            else:
                flags &= ~MODE_REFLECT
            res = buf
        if res:
            if not flags & MODE_REFLECT:
                self.dispatch(dest, res)
            else:
                self._log('put, dest=%s, src=%s' % (src, dest))
                self._dispatcher.sendto(src, dest, res, hidden=True, flags=flags)
        return True
    
    def save(self, name, buf):
        save_device(self._manager, name, buf)
        self._log('save, name=%s' % name)