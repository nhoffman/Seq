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

class TestRunClustalw(unittest.TestCase):
    
    def setUp(self):
        self.file1 = os.path.join(datadir, '10patients.fasta')
        self.funcname = '_'.join(self.id().split('.')[-2:])
        self.outfile = os.path.join(outputdir,self.funcname)
        
    def test1(self):
        # make the alignment
        
        aligned = self.outfile+'.aln'
        silent = True
        
        Seq.run_clustalw.run_clustalw(
            target_file=self.file1,
            run=True,
            align=None,
            batch=None,
            outfile=aligned,
            silent=silent)
              
        # make a tree
        Seq.run_clustalw.run_clustalw(
            target_file=aligned,
            run=True,
            tree=None,
            batch=None,
            outputtree='phylip',
            tossgaps=None,
            silent=silent)

        # make a bootstrap tree
        Seq.run_clustalw.run_clustalw(
            target_file=aligned,
            run=True,
            bootstrap=None,
            batch=None,
            outputtree='phylip',
            tossgaps=None,
            bootlabels='node',
            silent=silent)        


                
