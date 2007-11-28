#!/usr/local/bin/python

"""Module to run clustalw"""

__version__ = '$Id: run_clustalw.py 1513 2007-10-16 00:09:27Z n.hoffman $'

import os, sys, logging, commands
import sequtil

log = logging

def getparams(**args):
    return args

def run_clustalw(target_file, clustal_cmd='clustalw', run=True, **params):
    """Run clustalw -options for command line parameters"""
    
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
    args.append(clustal_cmd)
    for k,v in defaults.items():
        if v:
            args.append('-%s="%s"' % (k,v))
        else:
            args.append('-%s' % k)
    
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
    
def main():
    """
Test routine for clustalw module"""
    
    logging.basicConfig(level=logging.DEBUG, format='%(lineno)s %(levelname)s %(message)s', stream=sys.stdout)
    
    # assume clustalw in $PATH
    clustalwpath = 'clustalw'   
    
    fastafile = 'testfiles/10patients.fasta'
    
    log.warning('infile: %s' % fastafile)
    
    path, fname = os.path.split(fastafile)
    fname = os.path.splitext(fname)[0]
    
    path = '/tmp'
    
    aligned = os.path.join(path, fname + '.aln')
    treename = os.path.join(path, fname + '.ph')
    bootname = os.path.join(path, fname + '.phb')
    
    run = True
    
    # make the alignment
    run_clustalw(
        target_file=fastafile,
        run=run,
        align=None,
        batch=None,
        outfile=aligned)
            
    # make a tree
    run_clustalw(
        target_file=aligned,
        run=run,
        tree=None,
        batch=None,
        outputtree='phylip',
        tossgaps=None)

    # make a bootstrap tree
    run_clustalw(
        target_file=aligned,
        run=run,
        bootstrap=None,
        batch=None,
        outputtree='phylip',
        tossgaps=None,
        bootlabels='node')

    
    
if __name__ =='__main__':
    main()

