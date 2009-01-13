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

class TestSeqObject(unittest.TestCase):

    def setUp(self):
        self.file1 = open(os.path.join(datadir, '10patients.fasta')).read()

    def test1(self):
        name, seq = 'buh', 'ACGT'
        seq = Seq.Seq(name=name, seq=seq)
        self.assertTrue(seq.name == name)
        self.assertTrue(seq.seq == seq)


