#!/usr/local/bin/python

"""A thin wrapper around hmmer 2.x suite of tools ()"""

__version__ = '$Id$'

import os
import sys
import logging
import commands
import subprocess
import re

import sequtil

log = logging

def getparams(**args):
    return args

# def get_slices(line, slices):
#     return [line.__getslice__(*slice).strip() for slice in slices]
    
def parse_cmstats(input):
    
    if len(input) < 50 and os.access(input, os.F_OK):
        # assume input is a filename
        iterover = open(input)
        # assume input is a string
    else:
        iterover = input.splitlines()
    
    data = []
    headers = None
    slices = None
    for line in iterover:
        if line.startswith('# seq idx'):
            headers = line
        elif line.startswith('# ---') and headers:
            slices = [i.span() for i in re.finditer('-+',line)]
            get_slices = lambda line: [line.__getslice__(*slice).strip() for slice in slices]
            headers = ['_'.join(h.split()) for h in get_slices(headers)]
        elif line.strip() and not line.startswith('#') and slices:
            data.append( dict(zip(headers, get_slices(line))) )
    
    return data
        
def cmbuild(infile, outfile=None, defaults=None, quiet=False, dryrun=False, **params):

    infile = os.path.abspath(infile)
    
    if outfile:
        outfile = os.path.abspath(outfile)
    elif outfile is None:
        outfile = os.path.join(os.path.split(infile)[0], sequtil.randomname(length=10)+'.cm')
    
    stdoutdata, stderrdata = _run('cmbuild',
        F=None,
        args=[outfile, infile],
        quiet=quiet,
        dryrun=dryrun,
        **params)
        
    return outfile

def cmalign(cmfile, fastafile, outfile=None, statsfile=None, 
    defaults=None, quiet=False, dryrun=False, **params):

    cmfile = os.path.abspath(cmfile)
    fastafile = os.path.abspath(fastafile)
    
    if outfile:
        outfile = os.path.abspath(outfile)
    elif outfile is None:
        outfile = os.path.join(os.path.split(fastafile)[0], sequtil.randomname(length=10)+'.sto')
    
    stdoutdata, stderrdata = _run('cmalign',
        o=outfile,
        args=[cmfile, fastafile],
        quiet=quiet,
        dryrun=dryrun,
        **params)
    
    if not stderrdata and not dryrun:
        if not statsfile:
            statsfile = os.path.splitext(outfile)[0]+'.cmalign'
        open(statsfile,'w').write(stdoutdata)
        
        align_data = parse_cmstats(stdoutdata)
    else:
        outfile, align_data = None, None
    
    return outfile, align_data
    
def _run(runcmd, args=None, defaults=None, quiet=False, dryrun=False, **params):
    """
    Returns the name of the outfile.    
    
    * cmd - name of the executable
    * args - unmodified arguments appended to end of command line
    * dryrun - build the command line and quit
    * defaults - an optional dict of key=val parameters 
    * params - pass arguments as either key=val pairs, or as
      key='' if key has no argument
    """
    
    cmd = sequtil.find_exec(runcmd)
    if cmd is None:
        raise OSError('%s could not be found' % runcmd)
    
    os_type = sequtil.get_os_type()
    if os_type != 'POSIX':
        raise OSError('Operating system must be POSIX-like')
                
    if defaults is None:
        defaults = {}
    
    defaults.update(params)
    arguments = [cmd]
    for k,v in defaults.items():
        if len(k) == 1:
            dashes = '-'
        else:
            dashes = '--'

        if v is None or not v.strip():
            add = ['%(dashes)s%(k)s']
        else:
            add = ['%(dashes)s%(k)s', '%(v)s']
                
        arguments.extend([fstr % locals() for fstr in add])
    
    if args:
        arguments.extend(args)
         
    log.info(arguments)
        
    if dryrun:
        return None, None
    else:
        stdoutdata, stderrdata = subprocess.Popen(arguments, stdout=subprocess.PIPE).communicate()
        
        if not quiet:
            print stdoutdata
        
        return stdoutdata, stderrdata
