#!/usr/local/bin/python

"""Module to run clustalw"""

__version__ = '$Id$'

import os
import sys
import logging
import subprocess

import sequtil

log = logging

def getparams(**args):
    return args

def check_clustalw():
    """Try to find the clustalw executable. If it exists, print the version number.
    """
    
    retval = subprocess.call('clustalw -help')
    
def run(target_file, clustal_cmd='clustalw', run=True, silent=False, **params):
    """Run clustalw -options for command line parameters"""

    if sequtil.find_exec(clustal_cmd) is None:
        raise OSError('%s could not be found' % clustal_cmd)

    os_type = sequtil.get_os_type()
    log.debug('os type is set as %s' % os_type)
    
#   defaults = getparams(
#   align=None,
#   batch=None,
#   infile=target_file,
#   output='phylip',
#   outputtree='nj')
    
    target_file = os.path.abspath(target_file)
    defaults = getparams(infile=target_file)
    defaults.update(params)
    args = []
    args.append('"%s"'%clustal_cmd) # surround with quotes to accomodate spaces
    
    if os_type == 'POSIX':
        argchar='-'
    elif os_type == 'WINDOWS':
        argchar='/'
    
    for k,v in defaults.items():
        if v:
            args.append('%s%s="%s"' % (argchar,k,v))
        else:
            args.append('%s%s' % (argchar,k))
    
    if silent:
        args.append('> %s' % os.devnull)
        
    cmd = ' '.join(args)
    log.info(cmd)
        
    if run and os_type == 'POSIX':
        log.info('running clustalw: %s' % cmd)
        os.system( cmd )
    elif os_type == 'WINDOWS':
        cwd,_ = os.path.split(target_file)

        cmds = ['cd "%s"' % cwd, cmd]
        sequtil.run_bat(cmds, path=cwd, run=run)
        
    return cmd
    
# for backward compatibility
def run_clustalw(*args, **kwargs):
    log.info('run_clustalw.run_clustalw is deprecated: use run_clustalw.run instead')
    return run(*args, **kwargs)