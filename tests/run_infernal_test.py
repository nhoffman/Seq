#!/usr/bin/env python

import sys
import os
import unittest
import logging
import pprint

import config

import Seq

log = logging

module_name = os.path.split(sys.argv[0])[1].rstrip('.py')
outputdir = config.outputdir
datadir = config.datadir 

class TestInfernalInstalled(unittest.TestCase):
    def test1(self):
        if not Seq.find_exec('cmbuild'):
            log.error('Infernal software could not be found - skipping tests in this module')

class Test_Run(unittest.TestCase):
    
    def setUp(self):
        self.funcname = '_'.join(self.id().split('.')[-2:])
        self.outfile = os.path.join(outputdir,self.funcname)
        self.has_space = os.path.join(outputdir,'name with spaces')
        self.no_space = os.path.join(outputdir,'nameWithoutSpaces')
        
        os.system('echo `date` has space > "%s"' % self.has_space)
        os.system('echo `date` no space > "%s"' % self.no_space)
        
    def test1(self):        
        stdout, stderr = Seq.run_infernal._run('ls',        
            quiet=True)
    
    def test2(self):        
        stdout, stderr = Seq.run_infernal._run('diff',
            y='',
            args = [self.has_space, self.no_space],
            quiet=True)

class Test_parse_cmstats(unittest.TestCase):

    cmstats = """
# cmalign :: align sequences to an RNA CM
# INFERNAL 1.0rc5 (December 2008)
# Copyright (C) 2008 HHMI Janelia Farm Research Campus
# Freely distributed under the GNU General Public License (GPLv3)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# command: /usr/local/bin/cmalign --sub -o /Users/nhoffman/devel/Seq/test_output/Test_cmalign_test1.sto /Users/nhoffman/devel/Seq/testfiles/seed_16s_mini.cm /Users/nhoffman/devel/Seq/testfiles/3patients.fasta
# date:    Fri Jan  2 15:34:15 2009
#
# cm name                    algorithm  config  sub  bands     tau
# -------------------------  ---------  ------  ---  -----  ------
# seed_16s_mini-1              opt acc  global  yes    hmm   1e-07
#
#                                     bit scores                           
#                                 ------------------                       
# seq idx  seq name          len     total    struct  avg prob      elapsed
# -------  --------------  -----  --------  --------  --------  -----------
        1  F62024            469    374.89    127.81     0.923  00:00:00.31
        2  T70854            459    388.14    135.38     0.991  00:00:00.31
        3  T70854_revcomp    459   -110.56     49.93     0.545  00:00:00.69

# Alignment saved in file /Users/nhoffman/devel/Seq/test_output/Test_cmalign_test1.sto.
#
# CPU time: 1.39u 0.07s 00:00:01.46 Elapsed: 00:00:02
    """.strip()
    
    def test1(self):
        data = Seq.run_infernal.parse_cmstats(self.cmstats)
        log.info(pprint.pformat(data))
    
if Seq.find_exec('cmbuild') is not None:    
    class Test_cmalign(unittest.TestCase):
        
        def setUp(self):
            self.fastafile = os.path.join(datadir, '3patients.fasta')
            self.cmfile = os.path.join(datadir, 'seed_16s_mini.cm')
            self.funcname = '_'.join(self.id().split('.')[-2:])
            self.outfile = os.path.join(outputdir,self.funcname) + '.sto'                   
            try:
                os.remove(self.outfile)
            except OSError:
                pass
            
        def test1(self):
            outfile = Seq.run_infernal.cmalign(
                cmfile = self.cmfile,
                fastafile = self.fastafile,
                outfile = self.outfile,
                sub='',
                dryrun=False,
                quiet=True
                )
            self.assertTrue(os.access(outfile, os.F_OK))
                
    class Test_cmbuild(unittest.TestCase):
        
        def setUp(self):
            self.stofile = os.path.join(datadir, 'seed_16s_mini.sto')
            self.funcname = '_'.join(self.id().split('.')[-2:])
            self.outfile = os.path.join(outputdir,self.funcname) + '.cm'                   
            try:
                os.remove(self.outfile)
            except OSError:
                pass
        
        def test1(self):
            outfile = Seq.run_infernal.cmbuild(
                infile = self.stofile,
                outfile = self.outfile,
                dryrun=False,
                quiet=True                
                )
            self.assertTrue(os.access(outfile, os.F_OK))                