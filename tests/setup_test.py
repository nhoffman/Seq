#!/usr/bin/env python

import sys
import os
import time
import unittest
import logging
import pprint
import config

log = logging

module_name = os.path.split(sys.argv[0])[1].rstrip('.py')
outputdir = config.outputdir
datadir = config.datadir

class TestSetup(unittest.TestCase):

    def testDataDir(self):
        self.assertTrue(os.access(datadir, os.F_OK))

    def testOutputDir(self):
        self.assertTrue(os.access(outputdir, os.F_OK))

