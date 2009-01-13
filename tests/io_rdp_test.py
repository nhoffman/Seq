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

class TestReadRDPFasta(unittest.TestCase):

    def setUp(self):
        self.fasta1 = open(os.path.join(datadir, '10patients_rdpalign.fasta')).read()

    def test_readfasta10(self):
        seqs = Seq.io_rdp.read(self.fasta1)
        ##self.assertTrue(len(seqs) == 10)

    def test_readfasta11(self):
        seqs = Seq.io_rdp.read(self.fasta1, degap=True)
        ##self.assertTrue(len(seqs) == 10)

    def test_readfasta12(self):
        seqs = Seq.io_rdp.read(self.fasta1, style='upper')
        ##self.assertTrue(len(seqs) == 10)

