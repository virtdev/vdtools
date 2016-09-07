# probe.py
#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

from vdtools.dev.driver import Driver, wrapper

class Probe(Driver):
    @wrapper
    def put(self, *args, **kwargs):
        print('Probe: input=%s' % str(kwargs))
        return kwargs
