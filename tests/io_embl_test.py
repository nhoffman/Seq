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

class TestReadWriteEMBL(unittest.TestCase):

    def setUp(self):
        self.file1 = open(os.path.join(datadir, '242990_21.embl')).read()
        self.file2 = open(os.path.join(datadir, '246703_136.embl')).read()
        self.file3 = open(os.path.join(datadir, '246703_328.embl')).read()

    def test1(self):
        seqs = Seq.io_embl.read(self.file1)
        s = Seq.io_embl.write(seqs)

    def test2(self):
        seqs = Seq.io_embl.readEMBLStr(self.file1)
        s = Seq.io_embl.writeEMBLStr(seqs)


