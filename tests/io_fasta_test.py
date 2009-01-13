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

class TestReadFasta(unittest.TestCase):

    def setUp(self):
        self.fasta1 = open(os.path.join(datadir, '10patients.fasta')).read()

    def test_readfasta10(self):
        seqs = Seq.io_fasta.read(self.fasta1)
        self.assertTrue(len(seqs) == 10)

