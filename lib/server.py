#      server.py
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

import zerorpc
from util import zmqaddr
from parser import Parser
from conf.vdtools import BUILDER_PORT

class ServerHandler(object):
    def build(self, uid, path):
        parser = Parser(uid)
        return parser.build(path)

class Server(object):
    def run(self):
        srv = zerorpc.Server(ServerHandler())
        srv.bind(zmqaddr('0.0.0.0', BUILDER_PORT))
        srv.run()
