import os
import sys
import commands
from setuptools import setup, find_packages

_path = commands.getoutput('readlink -f %s' % sys.argv[0])
_dir = os.path.dirname(_path)
os.system(os.path.join(_dir, 'scripts', 'install.sh'))

setup(name='vdtools',
      version='0.0.1',
      description='A set of tools of virtdev',
      license="MIT",
      packages=find_packages(),
      package_data={'vdtools.drivers.kwget':['stoplist']},
     )
