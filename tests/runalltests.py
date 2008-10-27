#!/usr/bin/env python

import os, glob, logging, sys, re, unittest
log = logging

# import the test cases
for fname in glob.glob('*_test.py'):
    cmd = 'import %s' % fname[:-3]
    print cmd
    exec(cmd)

test_modules = [globals()[fn] for fn in dir() if re.search(r'_test$',fn)]
    
def main():
    
    loglevel = logging.WARNING
    # loglevel = logging.INFO
    
    logging.basicConfig(file=sys.stdout,
        format='%(levelname)s %(module)s %(funcName)s %(lineno)s %(message)s',
        ## format='%(message)s',
        level=loglevel)
    
    all_suites = [unittest.TestLoader().loadTestsFromModule(m) for m in test_modules]
    alltests = unittest.TestSuite(all_suites)
    unittest.TextTestRunner(verbosity=2).run(alltests)

if __name__ == '__main__':
    do_profile = False
    if do_profile:
        import cProfile, pstats
        cProfile.run('main()', 'prof')
        p = pstats.Stats('prof').strip_dirs()
        p.sort_stats('cumulative').print_stats(15)
    
        ## python -c "import pstats; pstats.Stats('prof').strip_dirs().sort_stats('cumulative').print_stats(15)"
    else:
        main()