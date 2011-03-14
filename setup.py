"""
Create unix package: python setup.py sdist
Create windows package: python setup.py bdist_wininst
"""

import glob
import re

from distutils.core import setup

def get_version(initfile):
    with open(initfile) as infile:
        instr = infile.read()
    return re.findall(r"__version__\s=\s'(\w+\.\w+\.\w+)'", instr)[0]

revision = '$Revision$'

params = {'name':'Seq',
          'version':get_version('__init__.py'),
          'packages':['Seq','taxonomy'],
          'package_dir':{'Seq':'.', 'taxonomy':'taxonomy'},
          'package_data':{'Seq': glob.glob('data/*')},
          'scripts':glob.glob('scripts/*.py'),
          'description':'Contains the Seq class and functions for manipulation of biological sequences',
          'author':'Noah Hoffman',
          'author_email':'noah.hoffman@gmail.com',
          'url':'https://github.com/nhoffman/Seq'
          }

setup(**params)

