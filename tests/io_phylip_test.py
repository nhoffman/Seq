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

    def test1(self):
        seqs = Seq.io_clustal.readAlnStr(self.file1)
        s = Seq.io_phylip.write(seqs)



