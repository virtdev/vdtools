#      combine.py
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

import sys
import argparse
from lib.common import combine

def usage():
    print 'combine.py -t timeout -d device1 device2 ...'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='timeout', default=None)
    parser.add_argument('-d', nargs='*', dest='devices', default=None)
    res = parser.parse_args(sys.argv[1:])
    timeout = res.timeout
    devices = res.devices
    if not devices or len(devices) < 2:
        usage()
        sys.exit()
    name = combine(devices, timeout)
    print 'combine: name=' + name