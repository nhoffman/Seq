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

class TestReadUSPTO(unittest.TestCase):

    def setUp(self):
        self.file1 = open(os.path.join(datadir, 'listing.uspto')).read()

    def test1(self):
        seqs = Seq.io_uspto.read(self.file1, matter='999999', client='888888')

    def test2(self):
        seqs = Seq.io_uspto.readSeqListing(self.file1, matter='999999', client='888888')



