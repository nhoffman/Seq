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

fastaname = os.path.join(datadir, '10patients.fasta')

class TestRunNeedle(unittest.TestCase):

    def setUp(self):
        self.seqs = Seq.io_fasta.read(open(fastaname).read())

    def test1(self):
        output = Seq.run_needle.needle(self.seqs[0], self.seqs[0:5])
        #Seq.run_needle.show_records(output)


