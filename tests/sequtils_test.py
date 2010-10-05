#!/usr/bin/env python

import sys
import os
import time
import unittest
import logging
import pprint
import config
import subprocess

log = logging

import Seq

module_name = os.path.split(sys.argv[0])[1].rstrip('.py')
outputdir = config.outputdir
datadir = config.datadir

class TestFunctions(unittest.TestCase):

    def test_find_exec(self):
        cmd = 'ls'
        path = Seq.find_exec(cmd)
        self.assertTrue(path)
        if path:
            out = subprocess.call([path], stdout=open(os.devnull,'w'))

        self.assertTrue(out == 0)


class TestReformatAlignment(unittest.TestCase):

    def setUp(self):
        fastr = open(os.path.join(datadir,'10patients_aln.fasta')).read()
        self.seqs = Seq.io_fasta.read(fastr)

    def tearDown(self):
        print ''
        for page in self.reform:
            for line in page:
                print line
            print ''

    def test01(self):
        self.reform = Seq.sequtil.reformat_alignment(self.seqs)

    def test02(self):
        self.reform = Seq.sequtil.reformat_alignment(
            self.seqs, exclude_invariant=True, min_subs=1)

    def test03(self):
        self.reform = Seq.sequtil.reformat_alignment(
            self.seqs, exclude_invariant=True, min_subs=1,
            seqrange=(50,500))

class TestReformat(unittest.TestCase):

    def setUp(self):
        fastr = open(os.path.join(datadir,'10patients_aln.fasta')).read()
        self.seqs = Seq.io_fasta.read(fastr)

    def tearDown(self):
        print ''
        for page in self.reform:
            for line in page:
                print line
            print ''

    def test01(self):
        self.reform = Seq.sequtil.reformat(self.seqs)

    def test02(self):
        self.reform = Seq.sequtil.reformat(
            self.seqs,
            exclude_invariant = True
            )

    def test03(self):
        self.reform = Seq.sequtil.reformat(
            self.seqs,
            exclude_invariant = False,
            seqrange = (50,100)
            )

    def test04(self):
        self.reform = Seq.sequtil.reformat(
            self.seqs,
            exclude_invariant = True,
            seqrange = (50,100)
            )

class TestCoalesce(unittest.TestCase):
    def setUp(self):
        self.funcname = '_'.join(self.id().split('.')[-2:])

    def test01(self):
        infile = os.path.join(datadir, '474_0_0.txt')
        names, seqs = zip(*(line.split() for line in open(infile) if line.strip()))
        
        d = Seq.sequtil.coalesce(seqs)
        parents = [seqs[i] for i in d.keys()]

        # canonical sequences should all be unique
        self.assertTrue(len(parents) == len(set(parents)))

        d1 = Seq.sequtil.coalesce(parents)
        self.assertTrue(len(d1) == len(parents))

        
        
        
