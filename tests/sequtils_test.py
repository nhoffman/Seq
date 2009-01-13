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
