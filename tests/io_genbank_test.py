#!/usr/bin/env python

import sys
import os
import time
import unittest
import logging
import pprint
import config

import Seq

log = logging

module_name = os.path.split(sys.argv[0])[1].rstrip('.py')
outputdir = config.outputdir
datadir = config.datadir

class TestReadGenbank1(unittest.TestCase):

    testfile = 'sequences.gb'
    
    def setUp(self):
        self.infile = os.path.join(datadir, self.testfile)
        self.instr = open(os.path.join(datadir, self.testfile)).read()
        self.seqs = list(Seq.io_genbank.read(self.infile))
        
    def test1(self):
        self.assertTrue(len(self.seqs)==self.instr.count('LOCUS'))
        
    def test2(self):
        for seq in self.seqs:
            seqlen = int(seq.data['LOCUS'][0].split()[1])
            self.assertTrue(len(seq) == seqlen)
            self.assertTrue(seq.taxid is not None and seq.taxid.isdigit())
            
class TestReadGenbank2(TestReadGenbank1):
    testfile = 'sequences2.gb'

# biopython_gb_files = '/home/bvdiversity/src/biopython/Tests/GenBank'
    
# class TestReadGenbank3(TestReadGenbank1):
#     testfile = os.path.join(biopython_gb_files, 'NC_000932.gb')

#     def test3(self):
#         seq = self.seqs[0]
#         pprint.pprint(seq.data)
    
