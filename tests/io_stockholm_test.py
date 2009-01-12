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

class TestReadStockholm(unittest.TestCase):

    def setUp(self):
        self.infile = os.path.join(datadir, '3patients.sto')
        self.instr = open(os.path.join(datadir, '3patients.sto')).read()

    def test1(self):
        seqs = Seq.io_stockholm.read(self.infile)

    def test2(self):
        seqs = Seq.io_stockholm.read(self.instr)
