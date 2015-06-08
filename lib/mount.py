#      mount.py
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
from lib.engine import Engine
from lib.util import close_port
from conf.virtdev import LO_PORT, FILTER_PORT, HANDLER_PORT, DISPATCHER_PORT, MOUNTPOINT

def _clean():
    close_port(LO_PORT)
    close_port(FILTER_PORT)
    close_port(HANDLER_PORT)
    close_port(DISPATCHER_PORT)

def mount():
    if not os.path.exists(MOUNTPOINT):
        os.makedirs(MOUNTPOINT, 0o755)
    _clean()
    engine = Engine()
    engine.start()
    engine.join()
