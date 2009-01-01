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

class TestThisModule(unittest.TestCase):
    
    def setUp(self):
        self.file1 = os.path.join(datadir, '10patients.fasta')
        self.funcname = '_'.join(self.id().split('.')[-2:])
        self.outfile = os.path.join(outputdir,self.funcname)
    
    def test1(self):
        raise Exception('not implemented')


                
