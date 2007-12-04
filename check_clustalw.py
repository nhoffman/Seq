#!/usr/local/bin/python

version = '$Id$'

import os, logging

log = logging

def get_os_type():
	"""
	Tries to guess the operating system type. Returns
	either 'POSIX' or 'WINDOWS'
	"""
	
	try:
		import _winreg
	except ImportError:
		os_type = 'POSIX'
	else:
		os_type = 'WINDOWS'
	
	return os_type

def clustal_search(dir_list, name):
	"""
	Parses a specified list of directories looking for clustalw executable
	"""

	for dir in dir_list:
		log.warning('searching directory %s' % dir)
		try:
			for root, dirs, items in os.walk(dir):
				for i in items:
					if i == name:
						return os.path.join(root,i)
					else:
						pass		
		except OSError:
			log.warning('directory %s not found' % dir)
			pass

def main():
	"""
	Returns path to clustalw or NONE
	"""
	os_type = get_os_type()
	
	if os_type == 'POSIX':
		"""
		look for clustalw in the following likely locations:
		/usr/bin/
		/usr/local/bin/
		/Users/*/local/bin/		
		/Users/*/Desktop/	
		"""
		user = os.environ['LOGNAME']
		dir_list = ['/usr/bin/','/usr/local/bin/', os.path.join('Users',user,'local','bin'), os.path.join('Users',user,'Desktop')]
		name = 'clustalw'
		
	elif os_type == 'WINDOWS':
		"""
		look for clustalw in the following likely locations:
		c:\Documents and Settings\*\Desktop
		c:\Program Files\clustalw
		c:\tools\
		"""
		user = os.environ['USERNAME']
		dir_list = [os.path.join('c:\\','Documents and Settings', user, 'Desktop'), os.path.join('c:\\', 'Program Files'), os.path.join('c:\\','tools')]	
		name = 'clustalw.exe'
		
	clustalpath = clustal_search(dir_list, name)
	if clustalpath:
		log.warning('clustalw found in directory %s' % clustalpath)
		return clustalpath
	else:
		log.warning('no clustalw program found.')
		return clustalpath
		
if __name__ == '__main__':
	main()