#!/usr/bin/env python

import sys
import os
import unittest
import logging

import config

import Seq

log = logging

module_name = os.path.split(sys.argv[0])[1].rstrip('.py')
outputdir = config.outputdir
datadir = config.datadir 

class TestHmmerInstalled(unittest.TestCase):
    def test1(self):
        if not Seq.run_hmmer.find_hmmcmd('hmmbuild'):
            log.error('hmm software could not be found - skipping tests in this module')

if Seq.run_hmmer.find_hmmcmd('hmmbuild') is not None:
    class TestRunHmmer(unittest.TestCase):
        
        def setUp(self):
            self.file1 = os.path.join(datadir, 's_trimmed.aln')
            self.funcname = '_'.join(self.id().split('.')[-2:])
            self.outfile = os.path.join(outputdir,self.funcname)
                    
        def test1(self):        
            outfile = Seq.run_hmmer.run('hmmbuild',
                infile=self.file1,
                outfile=self.outfile+'.hmm',
                F=None,
                dryrun=False,
                quiet=True)
            self.assertTrue(os.access(outfile, os.F_OK))
    
                    
