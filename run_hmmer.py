#!/usr/local/bin/python

"""A thin wrapper around hmmer 2.x suite of tools ()"""

__version__ = '$Id$'

import os
import sys
import logging
import commands
import subprocess

import sequtil

log = logging

def getparams(**args):
    return args

def find_hmmcmd(cmd, path=None):
    """
    Path is a list of directories possibly containing the executable.
    """

    if path is None:
        path = os.environ['PATH'].split(':')
    elif not hasattr(path, '__iter__'):
        path = [path]
    
    for pth in path:
        fasta = os.path.join(pth, cmd)
        if os.access(fasta, os.X_OK):
            return fasta
    
    return None

def run(hmmcmd, infile, outfile=False, dryrun=False, defaults=None, quiet=False, **params):
    """
    Returns the name of the outfile.    
    
    * cmd - choose one of hmmalign  hmmbuild  hmmcalibrate  
      hmmconvert  hmmemit  hmmfetch  hmmindex  hmmpfam  hmmsearch
    * infile - input file name
    * outfile - optional output file name. If False, no output file
      is specified; if None, output is written to a file given a random name.
    * dryrun - build the command line and quit
    * defaults - an optional dict of key=val parameters 
    * params - pass arguments as either key=val pairs, or as
      key=None if key is a command line switch
    """
    
    cmd = find_hmmcmd(hmmcmd)
    if cmd is None:
        raise OSError('%s could not be found' % hmmcmd)
    
    os_type = sequtil.get_os_type()
    log.debug('os type is set as %s' % os_type)
        
    infile = os.path.abspath(infile)
    if outfile: 
        outfile = os.path.abspath(outfile)
    elif outfile is None:
        outfile = os.path.join(os.path.split(infile)[0], sequtil.randomname(length=10))
    
    outin = [infile]
    if not outfile is False:
        outin.insert(0, outfile)
    
    if defaults is None:
        defaults = {}
    
    defaults.update(params)
    args = [cmd]
    for k,v in defaults.items():
        if len(k) == 1:
            dashes = '-'
        else:
            dashes = '--'
        
        if v is None:
            fstr = '%(dashes)s%(k)s'
        elif len(str(v).split()) > 1:
            fstr = '%(dashes)s%(k)s "%(v)s"'
        else:
            fstr = '%(dashes)s%(k)s %(v)s'
        
        args.append(fstr % locals())
    
    args.extend(outin)
        
    log.info(' '.join(args))
    
    if os_type == 'POSIX' and not dryrun:
        #subprocess.check_call(args)
        if quiet:
            stdout = open(os.devnull)
        else:
            stdout = None
        subprocess.Popen(args, stdout=stdout).communicate()
        
    elif os_type == 'WINDOWS':
        # completely untested
        cwd,_ = os.path.split(target_file)
        cmds = ['cd "%s"' % cwd, cmd]
        sequtil.run_bat(cmds, path=cwd, run=not dryrun)
        
    return outfile
    
def main():
    """
Test routine for clustalw module"""
    
    logging.basicConfig(level=logging.DEBUG, format='%(lineno)s %(levelname)s %(message)s', stream=sys.stdout)
        
    align = 'testfiles/s_trimmed.aln'
    log.warning('infile: %s' % align)
    
    path, fname = os.path.split(align)
    fname = os.path.splitext(fname)[0]
    
    path = 'test_output'
    try:
        os.mkdir(path)
    except OSError:
        pass
    
    hmm = os.path.join(path, fname + '.hmm')
    
    dryrun = False
    
    # make the alignment
    run('hmmbuild',
        infile=align,
        outfile=hmm,
        F=None,
        dryrun=dryrun)
               
if __name__ =='__main__':
    main()

