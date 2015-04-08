#      udo.py
#      
#      Copyright (C) 2014 Yi-Wei Ci <ciyiwei@hotmail.com>
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
import ast
import req
import time
from lib import stream
from datetime import datetime
from proc.loader import VDevLoader
from conf.virtdev import MOUNTPOINT
from lib.util import lock, mount_device
from threading import Thread, Event, Lock
from lib.log import log, log_get, log_err
from lib.op import OP_GET, OP_PUT, OP_OPEN, OP_CLOSE
from lib.mode import MODE_POLL, MODE_VIRT, MODE_SWITCH, MODE_REFLECT, MODE_SYNC, MODE_TRIG

LOG = True
FREQ_MAX = 100
FREQ_MIN = 0.01
OUTPUT_MAX = 1 << 22

class VDevUDO(object):
    def __init__(self, children={}):
        self._buf = {}
        self._event = {}
        self._lock = Lock()
        self._local = False
        self._children = children
        self._thread_listen = None
        self._thread_poll = None
        self._requester = None
        self.manager = None
        self._atime = None
        self._index = None
        self._sock = None
        self._name = None
        self._type = None
        self._uid = None
        self._range = {}
        self._mode = 0
        self._freq = 0
    
    def _log(self, text):
        if LOG:
            log(text)
    
    def _get_path(self):
        return os.path.join(MOUNTPOINT, self._uid, self._name)
    
    def _read(self):
        empty = (None, None)
        try:
            buf = stream.get(self._sock, self._local)
            if len(buf) > OUTPUT_MAX:
                return empty
        
            if not buf and self._local:
                return (self, '')
        
            output = ast.literal_eval(buf)
            if type(output) != dict:
                log_err(self, 'failed to read, invalid type, name=%s' % self.d_name)
                return empty
        
            if len(output) != 1:
                log_err(self, 'failed to read, invalid output, name=%s' % self.d_name)
                return empty
        
            if not output.has_key('None'):
                index = output.keys()[0]
                for i in self._children:
                    if self._children[i].d_index == int(index):
                        device = self._children[i]
                        break
                if not device:
                    log_err(self, 'failed to read, invalid index, name=%s' % self.d_name)
                    return empty
                output = output[index]
            else:
                device = self
                output = output['None']
            buf = device.check_output(output)
            return (device, buf)
        except:
            log_err(self, 'failed to read, name=%s' % self.d_name)
            return empty
    
    def _write(self, buf):
        if not buf:
            log_err(self, 'failed to write, empty buf')
            return
        try:
            stream.put(self._sock, buf, self._local)
            return True
        except:
            log_err(self, 'failed to write')
    
    def _mount(self):
        if self.d_mode & MODE_VIRT or self.d_index == None:
            mode = None
            freq = None
            prof = None
        else:
            mode = self._mode
            freq = self._freq
            prof = self.d_profile
            path = self._get_path()
            if os.path.exists(path):
                loader = VDevLoader(self._uid)
                curr_prof = loader.get_profile(self._name)
                if curr_prof['type'] == prof['type']:
                    curr_mode = loader.get_mode(self._name)
                    if ((curr_mode | MODE_SYNC) == (mode | MODE_SYNC)) and curr_prof.get('range') == prof.get('range'):
                        mode = None
                        freq = None
                        prof = None
                    else:
                        if not (curr_mode & MODE_SYNC):
                            mode &= ~MODE_SYNC
                        else:
                            mode |= MODE_SYNC
                        freq = loader.get_freq(self._name)
        mount_device(self._uid, self.d_name, mode, freq, prof)
    
    @lock
    def _check_device(self, device):
        if device.check_atime():
            index = device.d_index
            if None == index:
                index = 0
            self._write(req.req_get(index))
    
    def _poll(self):
        if not self.d_mode & MODE_POLL or not self._sock:
            return
        
        while True:
            try:
                time.sleep(self.d_intv)
                if self._children:
                    for i in self._children:
                        child = self._children[i]
                        if child.d_mode & MODE_POLL:
                            self._check_device(child)
                elif self.d_mode & MODE_POLL:
                    self._check_device(self)
            except:
                log_err(self, 'failed to poll')
                break
    
    @property
    def d_name(self):
        return self._name
    
    @property
    def d_mode(self):
        if not self.manager or self._children:
            return self._mode
        else:
            try:
                return self.manager.synchronizer.get_mode(self.d_name)
            except:
                return self._mode
    
    @property
    def d_freq(self):
        if not self.manager or self._children:
            return self._freq
        else:
            try:
                return self.manager.synchronizer.get_freq(self.d_name)
            except:
                return self._freq
    
    @property
    def d_index(self):
        return self._index
    
    @property
    def d_range(self):
        return self._range
    
    @property
    def d_type(self):
        if not self._type:
            return self.__class__.__name__
        else:
            return self._type
    
    @property
    def d_intv(self):
        freq = self.d_freq
        if freq > 0:
            return 1.0 / freq
        else:
            log_err(self, 'invalid frequency')
            raise Exception(log_get(self, 'invalid frequency'))
    
    @property
    def d_profile(self):
        prof = {}
        prof.update({'type':self.d_type})
        prof.update({'range':self.d_range})
        prof.update({'index':self.d_index})
        return prof
    
    def set_type(self, val):
        self._type = val
    
    def set_freq(self, val):
        if val > FREQ_MAX:
            self._freq = FREQ_MAX
        elif val < FREQ_MIN:
            self._freq = FREQ_MIN
        else:
            self._freq = val
    
    def set_range(self, val):
        self._range = dict(val)
    
    def set_index(self, val):
        self._index = int(val)
        
    def set_mode(self, val):
        self._mode = int(val)
    
    def set_local(self):
        self._local = True
    
    def find(self, name):
        if self.d_name == name:
            return self
        else:
            return self._children.get(name)
    
    def check_atime(self):
        now = datetime.now()
        if self._atime:
            intv = (now - self._atime).total_seconds()
            if intv >= self.d_intv:
                self._atime = now
                return True
        else:
            self._atime = now
    
    def check_output(self, output):
        for i in output:
            r = self._range.get(i)
            if not r:
                continue
            try:
                val = output[i]
                if (type(val) == int or type(val) == float) and (val < r[0] or val > r[1]):
                    log_err(self, 'invalid output, out of range')
                    return
            except:
                log_err(self, 'invalid output')
                return
        return output
    
    def sync(self, buf):
        if type(buf) != str and type(buf) != unicode:
            buf = str(buf)
        path = self._get_path()
        if os.path.exists(path):
            with open(path, 'wb') as f:
                f.write(buf)
            return True
    
    def _register(self, name):
        self._buf[name] = None
        self._event[name] = Event()
    
    def _set(self, device, buf):
        name = device.d_name
        if self._event.has_key(name):
            event = self._event[name]
            if not event.is_set():
                self._buf[name] = buf
                event.set()
                return True
    
    def _wait(self, name):
        self._event[name].wait()
        buf = self._buf[name]
        del self._buf[name]
        del self._event[name]
        return buf
    
    @lock
    def proc(self, name, op, buf=None):
        dev = self.find(name)
        if not dev:
            log_err(self, 'failed to process, cannot find device')
            return
        index = dev.d_index
        if op == OP_OPEN:
            if dev.d_mode & MODE_SWITCH:
                self._write(req.req_open(index))
        elif op == OP_CLOSE:
            if dev.d_mode & MODE_SWITCH:
                self._write(req.req_close(index))
        elif op == OP_GET:
            self._register(name)
            self._write(req.req_get(index))
            return self._wait(name)
        elif op == OP_PUT:
            self._register(name)
            self._write(req.req_put(index, str(buf[buf.keys()[0]])))
            return self._wait(name) 
        else:
            log_err(self, 'failed to process, invalid operation')
    
    def mount(self, manager, name, sock=None, init=True):
        self.manager = manager
        self._uid = manager.uid
        self._name = name
        self._sock = sock
        if self._children:
            self._mode |= MODE_VIRT
        if not self.d_freq:
            if self._children:
                poll = False
                for i in self._children:
                    if self._children[i].d_mode & MODE_POLL:
                        poll = True
                        break
                if poll:
                    self._freq = FREQ_MAX
                    self._mode |= MODE_POLL
            elif self._mode & MODE_POLL:
                self._freq = FREQ_MIN
        if init:
            self._mount()
        self._thread_poll = Thread(target=self._poll)
        self._thread_poll.start()
        self._thread_listen = Thread(target=self._listen)
        self._thread_listen.start()
        self._log('mount: type=%s [%s*]' % (self.d_type, self.d_name[:8]))
    
    def _listen(self):
        if not self._sock:
            return
        
        while True:
            try:
                device, buf = self._read()
                if not device:
                    continue
                
                name = device.d_name
                if self.manager.synchronizer.has_callback(name):
                    output = self.manager.synchronizer.callback(name, {name:buf})
                    if not output:
                        continue
                    
                    buf = ast.literal_eval(output)
                    if type(buf) != dict:
                        log_err(self, 'invalid result of callback function')
                        continue
                    
                    if buf:
                        mode = device.d_mode
                        if mode & MODE_REFLECT:
                            op = self.manager.synchronizer.get_oper({name:buf}, mode)
                            if op != None:
                                buf = self.proc(name, op)
                
                if not self._set(device, buf) and buf:
                    mode = device.d_mode
                    if not (mode & MODE_TRIG) or device.check_atime():
                        if mode & MODE_SYNC:
                            device.sync(buf)
                        self.manager.synchronizer.dispatch(name, buf)
            except:
                log_err(self, 'device=%s, restarting' % self.d_name)
                try:
                    self._sock.close()
                except:
                    pass
                break
    