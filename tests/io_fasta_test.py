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

    fasta1 = os.path.join(datadir, '10patients.fasta')

    def setUp(self):
        self.funcname = '_'.join(self.id().split('.')[-2:])
        self.outname = os.path.join(outputdir, self.funcname) + '.fasta'
        log.info('writing %s' % self.outname)

    def tearDown(self):
        ## perform exhaustive test here
        self.assertTrue(len(self.seqs) == self.nseqs)
        self.assertTrue(len(self.seqs2) == self.nseqs)

        for s1,s2 in zip(self.seqs, self.seqs2):
            self.assertTrue(s1.name == s1.name)
            self.assertTrue(s1.seq == s1.seq)

    def test_readfasta10(self):
        # read it
        instr = open(self.fasta1).read()
        self.nseqs = instr.count('>')
        self.seqs = Seq.io_fasta.read(instr)

        # write it
        fout = open(self.outname,'w')
        fout.write(Seq.io_fasta.write(self.seqs))
        fout.close()

        # read it back in
        self.seqs2 = Seq.io_fasta.read(open(self.outname).read())


    def test_readfasta20(self):
        # read it
        instr = open(self.fasta1).read()
        self.nseqs = instr.count('>')
        self.seqs = Seq.io_fasta.read(instr)

        # write it
        fout = open(self.outname,'w')
        fout.write(Seq.io_fasta.write(self.seqs, linelength=None))
        fout.close()

        # read it back in
        self.seqs2 = Seq.io_fasta.read(open(self.outname).read())
