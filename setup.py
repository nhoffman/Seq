"""
Create unix package: python setup.py sdist
Create windows package: python setup.py bdist_wininst
"""

from distutils.core import setup
import glob, os, sys

revision = '$Revision: 1557 $'

files = ['__init__.py','Sequence.py','Dictionaries.py','sequtil.py']
files.extend(glob.glob('io_*.py'))
files.extend(glob.glob('run_*.py'))

site_packages = os.path.join(sys.prefix, 'lib', 'python'+sys.version[:3],'site-packages')

_,_,files_in_data = os.walk('data').next()
files_in_data = ['data/%s'%f for f in files_in_data]
data_dir = os.path.join(site_packages,'Seq','data')

_,_,files_in_testfiles = os.walk('testfiles').next()
files_in_testfiles = ['testfiles/%s'%f for f in files_in_testfiles]
testfiles_dir = os.path.join(site_packages,'Seq','testfiles')

setup(name='Seq',
      version = revision[:-1].split(':')[1].strip(),
      packages = ['Seq'],
      package_dir = {'Seq':'.'},
      data_files=[(data_dir, files_in_data),(testfiles_dir, files_in_testfiles)],
      #py_modules = modules,
      description = 'Contains the Seq class and functions for manipulation of biological sequences',
      author = 'Noah Hoffman',
      author_email = 'noah.hoffman@gmail.com',
      url = 'http://staff.washington.edu/ngh2',
      )

