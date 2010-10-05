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

class TestWritePhylip(unittest.TestCase):

    def setUp(self):
        self.file1 = open(os.path.join(datadir, 'oscillo_F41669_top20.aln')).read()
        self.seqs = Seq.io_clustal.read(self.file1)

    def test1(self):
        s = Seq.io_phylip.write(self.seqs)
        log.info(s[:1000])

    def test2(self):
        s = Seq.io_phylip.write(self.seqs, width=None)
        log.info(s[:1000])

    def test3(self):
        s = Seq.io_phylip.write(self.seqs, renum=True)
        log.info(s[:1000])


