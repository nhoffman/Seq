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

class TestReadGenbank(unittest.TestCase):

    def setUp(self):
        self.infile = os.path.join(datadir, 'sequences.gb')
        self.instr = open(os.path.join(datadir, 'sequences.gb')).read()

    def test1(self):
        seqs = Seq.io_genbank.read(self.infile)
        for seq in seqs:
            print seq.name, seq.data['FEATURES'][1]['source'][1]['db_xref'][0]



