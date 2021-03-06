# udo.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import os
import ast
import time
from vdtools.lib import io
from datetime import datetime
from vdtools.conf.log import LOG_UDO
from vdtools.lib.loader import Loader
from vdtools.conf.defaults import UPLOAD
from threading import Thread, Event, Lock
from vdtools.lib.log import log_debug, log_err
from vdtools.lib.util import lock, get_mnt_path
from vdtools.lib.attributes import ATTR_MODE, ATTR_FREQ
from vdtools.dev.driver import FREQ_MAX, FREQ_MIN, need_freq
from vdtools.lib.cmd import cmd_get, cmd_put, cmd_open, cmd_close
from vdtools.lib.operations import OP_GET, OP_PUT, OP_OPEN, OP_CLOSE
from vdtools.lib.modes import MODE_VIRT, MODE_SWITCH, MODE_SYNC, MODE_TRIG

RETRY_MAX = 3
WAIT_TIME = 10 #seconds
SLEEP_TIME = 10 # seconds
OUTPUT_MAX = 1 << 22
POLL_INTERVAL = 0.01  # seconds

class UDO(object):
    def __init__(self, children={}, local=False):
        self._buf = {}
        self._events = {}
        self._lock = Lock()
        self._local = local
        self._freq = FREQ_MAX
        self._write_lock = Lock()
        self._children = children
        self._requester = None
        self._listener = None
        self._active = False
        self._idle = Event()
        self._poller = None
        self._socket = None
        self._atime = None
        self._index = None
        self._core = None
        self._name = None
        self._type = None
        self._uid = None
        self._spec = {}
        self._mode = 0

    def _log(self, text):
        if LOG_UDO:
            log_debug(self, text)

    @property
    def d_name(self):
        return self._name

    @property
    def d_mode(self):
        if not self._core or self._children:
            return self._mode
        else:
            cnt =  RETRY_MAX
            while True:
                mode = self._core.get_mode(self.d_name)
                if mode != None:
                    self._mode = mode
                    return mode
                cnt -= 1
                if cnt > 0:
                    time.sleep(SLEEP_TIME)
                else:
                    break
            log_err(self, 'failed to get mode, type=%s, name=%s' % (self.d_type, self.d_name))
            return self._mode

    @property
    def d_freq(self):
        if not self._core or self._children:
            return self._freq
        else:
            for i in range(RETRY_MAX + 1):
                freq = self._core.get_freq(self.d_name)
                if freq != None:
                    self._freq = freq
                    return freq
                elif i < RETRY_MAX:
                    time.sleep(SLEEP_TIME)
            log_err(self, 'failed to get freq, type=%s, name=%s' % (self.d_type, self.d_name))
            return self._freq

    @property
    def d_index(self):
        return self._index

    @property
    def d_spec(self):
        return self._spec

    @property
    def d_type(self):
        return self._type

    @property
    def d_intv(self):
        freq = self.d_freq
        if freq > 0:
            return 1.0 / freq
        else:
            return float('inf')

    @property
    def d_profile(self):
        prof = {}
        prof.update({'type':self._type})
        prof.update({'spec':self._spec})
        prof.update({'index':self._index})
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

    def set_spec(self, val):
        self._spec = dict(val)

    def set_index(self, val):
        self._index = int(val)

    def set_mode(self, val):
        self._mode = int(val)

    def set_active(self):
        self._active = True

    def set_inactive(self):
        self._active = False

    def set_busy(self):
        self._idle.clear()

    def set_idle(self):
        self._idle.set()

    def wait(self):
        self._idle.wait(WAIT_TIME)

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
            item = self._spec.get(i)
            if not item:
                continue
            try:
                val = output[i]
                typ = item['type']
                if (type(val) == int or type(val) == float) and type(typ) == list and (val < typ[0] or val > typ[1]):
                    log_err(self, 'failed to check output')
                    return
            except:
                log_err(self, 'failed to check output')
                return
        return output

    def _add_event(self, name):
        self._buf[name] = None
        self._events[name] = Event()

    def _del_event(self, name):
        del self._events[name]

    def _put(self, device, buf):
        if not device:
            return
        name = device.d_name
        if self._events.has_key(name):
            event = self._events[name]
            if not event.is_set():
                self._buf[name] = buf
                event.set()
                return True

    def _get(self, name):
        self._events[name].wait()
        buf = self._buf[name]
        del self._buf[name]
        del self._events[name]
        return buf

    def get_index(self):
        index = self.d_index
        if index != None:
            return index
        else:
            return 0

    def _read_device(self):
        empty = (None, None)
        try:
            buf = io.get(self._socket, self._local)
            if len(buf) > OUTPUT_MAX or not buf:
                return empty

            output = ast.literal_eval(buf)
            if type(output) != dict:
                log_err(self, 'failed to read device, cannot parse, type=%s, name=%s' % (self.d_type, self.d_name))
                return empty

            if len(output) != 1:
                log_err(self, 'failed to read device, invalid length, type=%s, name=%s' % (self.d_type, self.d_name))
                return empty

            device = None
            index = output.keys()[0]
            output = output[index]
            if self._children:
                for i in self._children:
                    if self._children[i].d_index == int(index):
                        device = self._children[i]
                        break
            elif 0 == index:
                device = self

            if not device:
                log_err(self, 'failed to read device, cannot get device, type=%s, name=%s' % (self.d_type, self.d_name))
                return empty

            buf = device.check_output(output)
            return (device, buf)
        except:
            log_err(self, 'failed to read device, type=%s, name=%s' % (self.d_type, self.d_name))
            return empty

    def _write_device(self, buf):
        if not buf:
            log_err(self, 'failed to write device, no data, type=%s, name=%s' % (self.d_type, self.d_name))
            return
        self._write_lock.acquire()
        try:
            io.put(self._socket, buf, self._local)
            return True
        except:
            log_err(self, 'failed to write device, type=%s, name=%s' % (self.d_type, self.d_name))
        finally:
            self._write_lock.release()

    def _check_device(self, device=None):
        if not device:
            device = self
        device.wait()
        if device.check_atime():
            device.set_busy()
            index = device.get_index()
            if not self._write_device(cmd_get(index)):
                device.set_idle()

    def can_poll(self):
        return need_freq(self.d_mode)

    def _poll(self):
        try:
            while True:
                time.sleep(POLL_INTERVAL)
                if self._children:
                    for i in self._children:
                        child = self._children[i]
                        if child.can_poll():
                            self._check_device(child)
                elif self.can_poll():
                    self._check_device()
        except:
            log_err(self, 'failed to poll, type=%s, name=%s' % (self.d_type, self.d_name))

    def _handle(self, device, buf):
        if not self._put(device, buf) and buf:
            mode = device.d_mode
            if not (mode & MODE_TRIG) or device.check_atime():
                res = None
                name = device.d_name
                if mode & MODE_SYNC and UPLOAD:
                    try:
                        self._core.save(name, buf)
                    except:
                        log_err(self, 'failed to handle, cannot save, name=%s' % name)
                        return
                if self._core.has_handler(name):
                    try:
                        res = self._core.handle(name, {name:buf})
                    except:
                        log_err(self, 'failed to handle, name=%s' % name)
                        return
                else:
                    res = buf
                if res:
                    try:
                        self._core.dispatch(name, res)
                    except:
                        log_err(self, 'failed to handle, cannot dispatch, name=%s' % name)

    def _listen(self):
        try:
            while True:
                device, buf = self._read_device()
                if device:
                    try:
                        self._handle(device, buf)
                    except:
                        log_err(self, 'failed to listen, cannot handle, type=%s, name=%s' % (self.d_type, self.d_name))
                    finally:
                        device.set_idle()
        except:
            log_err(self, 'failed to listen, type=%s, name=%s' % (self.d_type, self.d_name))
            io.close(self._socket)

    def _start(self):
        if self._socket:
            self._poller = Thread(target=self._poll)
            self._poller.start()
            self._listener = Thread(target=self._listen)
            self._listener.start()

    def _mount(self):
        if self._children:
            self._mode |= MODE_VIRT

        if self._mode & MODE_VIRT or self._index == None:
            mode = None
            freq = None
            prof = None
        else:
            mode = self._mode
            freq = self._freq
            prof = self.d_profile
            path = get_mnt_path(self._uid, self._name)
            if os.path.exists(path):
                loader = Loader(self._uid)
                curr_prof = loader.get_profile(self._name)
                if curr_prof['type'] == prof['type']:
                    curr_mode = loader.get_attr(self._name, ATTR_MODE, int)
                    if ((curr_mode | MODE_SYNC) == (mode | MODE_SYNC)) and curr_prof.get('spec') == prof.get('spec'):
                        mode = None
                        freq = None
                        prof = None
                    else:
                        if not (curr_mode & MODE_SYNC):
                            mode &= ~MODE_SYNC
                        else:
                            mode |= MODE_SYNC
                        freq = loader.get_attr(self._name, ATTR_FREQ, float)

    def mount(self, uid, name, core, sock=None, init=True):
        self._uid = uid
        self._name = name
        self._core = core
        self._socket = sock
        if init:
            self._mount()
        self._start()

    def _check_args(self, buf):
        try:
            if not buf or type(buf) != dict:
                log_err(self, 'invalid arguments')
                return
            args = []
            kwargs = {}
            for i in buf:
                val = buf[i]
                if type(val) == dict:
                    kwargs.update(val)
                elif type(val) == list or type(val) == str or type(val) == unicode:
                    args.append(val)
                else:
                    log_err(self, 'invalid arguments')
                    return
            return str({'args':args, 'kwargs':kwargs})
        except:
            log_err(self, 'invalid arguments');

    @lock
    def proc(self, name, op, buf=None):
        if not self._socket:
            return

        device = self.find(name)
        if not device:
            log_err(self, 'failed to process, cannot find device, name=%s' % str(name))
            return

        index = device.d_index
        try:
            if op == OP_OPEN:
                if device.d_mode & MODE_SWITCH:
                    if self._write_device(cmd_open(index)):
                        self._log('open, type=%s, name=%s' % (device.d_type, device.d_name))
            elif op == OP_CLOSE:
                if device.d_mode & MODE_SWITCH:
                    if self._write_device(cmd_close(index)):
                        self._log('close, type=%s, name=%s' % (device.d_type, device.d_name))
            elif op == OP_GET:
                self._add_event(name)
                if self._write_device(cmd_get(index)):
                    self._log('get, type=%s, name=%s' % (device.d_type, device.d_name))
                    return self._get(name)
                else:
                    self._del_event(name)
            elif op == OP_PUT:
                self._add_event(name)
                val = self._check_args(buf)
                if val:
                    if self._write_device(cmd_put(index, val)):
                        self._log('put, type=%s, name=%s' % (device.d_type, device.d_name))
                        return self._get(name)
                    else:
                        self._del_event(name)
            else:
                log_err(self, 'failed to process, invalid operation, type=%s, name=%s' % (device.d_type, device.d_name))
        except:
            log_err(self, 'failed to process, type=%s, name=%s' % (device.d_type, device.d_name))
            io.close(self._socket)
            self._socket = None
