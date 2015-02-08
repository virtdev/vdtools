#      deploy.py
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

import os
import sys
from lib.compiler import VDCompiler

def usage():
    print 'deploy.py path [-v] [uid]'
    print '-v: deploy to vdfs'
    
if __name__ == '__main__':
    argc = len(sys.argv)
    if (argc != 2 and argc != 4) or not os.path.isdir(sys.argv[1]) or (argc == 4 and sys.argv[2] != '-v'):
        usage()
        sys.exit()
    
    if argc == 4:
        compiler = VDCompiler(sys.argv[3])
    else:
        compiler = VDCompiler()
    
    ret = compiler.compile(sys.argv[1])
    print 'deploy: ret=%s' % str(ret)
