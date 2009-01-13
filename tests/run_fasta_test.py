#!/usr/bin/env python

import sys
import os
import unittest
import logging
import pprint

import config

import Seq

log = logging

module_name = os.path.split(sys.argv[0])[1].rstrip('.py')
outputdir = config.outputdir
datadir = config.datadir

fasta_path = Seq.find_exec('fasta35')

class TestFastaInstalled(unittest.TestCase):
    def test1(self):
        if fasta_path is None:
            log.error('fasta35 could not be found - skipping tests in this module')


if fasta_path is not None:
    class TestRunFasta(unittest.TestCase):

        def setUp(self):
            self.file1 = os.path.join(datadir, '10patients.fasta')
            self.funcname = '_'.join(self.id().split('.')[-2:])
            self.outfile = os.path.join(outputdir,self.funcname)

        def test1(self):
            seqs = Seq.io_fasta.read(open(self.file1).read())
            query, target = seqs[0], seqs[1:]
            output = Seq.run_fasta.run(query, target, outfile=self.outfile)
