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
    
    def setUp(self):
        self.fasta1 = open(os.path.join(datadir, '10patients.fasta')).read()
        
    def test_readfasta10(self):
        seqs = Seq.io_fasta.read(self.fasta1)        
        self.assertTrue(len(seqs) == 10)
                
def main():
    """
    Usage: thisfile.py [method-name]
    
    Runs all unit tests defined in classes in this module;
    can also run a single method if a name is provided
    as the first argument.
    """
    
    #debuglevel = logging.DEBUG
    debuglevel = config.debuglevel
    
    logging.basicConfig(file=sys.stdout,
        format='%(levelname)s %(module)s %(funcName)s %(lineno)s %(message)s',
        ## format='%(message)s',
        level=debuglevel)
    
    try:        
        method = sys.argv[1]
        classnames = [k for k,v in globals().items() if hasattr(v, 'assertEquals')]
        for classname in classnames:
            try:
                module = module_name
                loadname = '%(module)s.%(classname)s.%(method)s'%locals()
                suites = [unittest.TestLoader().loadTestsFromName(loadname)]
            except AttributeError:
                pass
            else:
                break
    except IndexError:
        classobjs = [v for k,v in globals().items() if hasattr(v, 'assertEquals')]
        
        suites = [unittest.TestLoader().loadTestsFromTestCase(co) for co in classobjs]

    ## assemble all test suites and run
    alltests = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(alltests)

if __name__ == '__main__':
    do_profile = False
    if do_profile:
        profname = os.path.join(outputdir, module_name + '.prof')
        import cProfile, pstats
        cProfile.run('main()', profname)
        p = pstats.Stats(profname).strip_dirs()
        p.sort_stats('cumulative').print_stats(15)
    
        ## python -c "import pstats; pstats.Stats('prof').strip_dirs().sort_stats('cumulative').print_stats(15)"
    else:
        main()
