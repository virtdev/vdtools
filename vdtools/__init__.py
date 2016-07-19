import os
import uuid
import xattr
import zerorpc
from vdtools.lib.simulator import Simulator
from vdtools.conf.vdtools import SIMULATOR_PORT
from vdtools.conf.env import PATH_MNT, PATH_VDEV
from vdtools.lib.modes import MODE_VIRT, MODE_CLONE
from vdtools.lib.operations import OP_ENABLE, OP_DISABLE
from vdtools.lib.util import DEFAULT_UID, zmqaddr, edge_dir, close_port
from vdtools.conf.virtdev import LO_PORT, FILTER_PORT, HANDLER_PORT, DISPATCHER_PORT

VDEV = 'VDev'

def check_uuid(identity):
    try:
        return uuid.UUID(identity).hex
    except:
        return

def create(typ, uid=DEFAULT_UID, parent=None):
    if uid == DEFAULT_UID:
        mode = MODE_VIRT
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, None, None, None, None, None, None, None, typ, None)
        cli.close()
    else:
        attr = {}
        attr['type'] = typ
        if parent:
            attr['parent'] = parent
        path = os.path.join(PATH_VDEV, uid)
        name = xattr.getxattr(path, 'create:%s' % str(attr))
    return name

def clone(parent, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        mode = MODE_CLONE
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, None, parent, None, None, None, None, None, None, None)
        cli.close()
    else:
        attr = {'parent':parent}
        path = os.path.join(PATH_VDEV, uid)
        name = xattr.getxattr(path, 'clone:%s' % str(attr))
    return name

def combine(vrtx, timeout, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        mode = MODE_VIRT
        name = uuid.uuid4().hex
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.create(uid, name, mode, vrtx, None, None, None, None, None, None, None, timeout)
        cli.close()
    else:
        attr = {}
        attr['vertex'] = vrtx
        attr['timeout'] = timeout
        path = os.path.join(PATH_VDEV, uid)
        name = xattr.getxattr(path, 'combine:%s' % str(attr))
    return name

def enable(name, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.enable(name)
        cli.close()
    else:
        path = os.path.join(PATH_VDEV, uid, name)
        xattr.setxattr(path, OP_ENABLE, '')

def disable(name, uid=DEFAULT_UID):
    if uid == DEFAULT_UID:
        cli = zerorpc.Client()
        cli.connect(zmqaddr('127.0.0.1', SIMULATOR_PORT))
        cli.disable(name)
        cli.close()
    else:
        path = os.path.join(PATH_VDEV, uid, name)
        xattr.setxattr(path, OP_DISABLE, '')

def link(src, dest, uid=DEFAULT_UID):
    if not check_uuid(src) or not check_uuid(dest):
        print 'invalid identity'
        return False
    if uid == DEFAULT_UID:
        path = edge_dir(uid, src)
    else:
        path = os.path.join(PATH_VDEV, uid, 'edge', src)
    os.system('touch %s' % os.path.join(path, dest))
    return True

def clean():
    os.system('rm -rf %s' % PATH_MNT)

def mount():
    if not os.path.exists(PATH_MNT):
        os.makedirs(PATH_MNT, 0o755)
    close_port(LO_PORT)
    close_port(FILTER_PORT)
    close_port(HANDLER_PORT)
    close_port(DISPATCHER_PORT)
    simu = Simulator()
    simu.start()
    simu.join()
