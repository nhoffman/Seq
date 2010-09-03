#!/usr/bin/env python

"""
I/O for pplacer output files.

For a decsription of the pplacer file format, see

http://matsen.fhcrc.org/pplacer/manual.html#placefile
"""

__version__ = "$Id$"

import re
import os
import sys
import logging
from collections import defaultdict
import itertools

log = logging

colnames = ('name','hit','at','mlwr','ppost','mlll','bml','edge','branch')

def read(fname):

    """
    Return an iterator over the data in the specified .place file.
    Fields are as follows (3-9 defined in the pplacer manual):

    1. name: sequence name
    2. hit: an integer in [1,N] indicating the number of the hit.
    3. Placement edge number, numbered as in a postorder traversal
    4. ML likelihood weight ratio (i.e. the normalized ML likelihood values)
    5. Posterior probability (or a dash if the -p option was not set)
    6. ML log likelihood
    7. Bayes marginal likelihood (or a dash if the -p option was not set)
    8. The ML distance from the distal (farthest from the root) side of the edge
    9. The ML pendant branch length
    """

    # indices of fields possibly occupied by a '-'
    ppost = colnames.index('ppost')
    bml = colnames.index('bml')

    undash = lambda e: e if e != '-' else None

    counter = itertools.count
    with open(fname) as lines:
        data = []
        skip = False
        for line in lines:
            if line.startswith('#'):
                continue
            elif skip:
                skip = False
            elif line.startswith('>'):
                if data:
                    yield data
                seqname = line.strip('\n >')
                skip = True ## skip the next line (the sequence string)
                data = []
                count = counter(1)
            else:
                L = [seqname, str(count.next())] + line.split()
                L[ppost], L[bml] = undash(L[ppost]), undash(L[bml])
                data.append(L)

                # try:
                #     L = [seqname, str(count.next())] + line.split()
                #     L[ppost], L[bml] = undash(L[ppost]), undash(L[bml])
                #     data.append(L)
                # except IndexError:
                #     log.error('error reading line in placefile: \n--->\n%s\n<---\n' % line)
                #     break

        yield data

def main():

    """
Usage: %s placefile [outfile]

Write tab-delimited file containing data in placefile to outfile
(or stdout in the absence of a second argument).
""" % os.path.split(sys.argv[0])[1]

    try:
        fname = sys.argv[1]
        if fname.lower().strip('-').startswith('h'):
            raise IndexError
    except IndexError:
        sys.exit(__doc__)

    try:
        outname = sys.argv[2]
        fout = open(outname, 'w')
    except IndexError:
        fout = sys.stdout

    sep = '\t'
    fout.write(sep.join(colnames) + '\n')
    fout.write('\n'.join(sep.join(r) for r in itertools.chain(*read(fname))) + '\n')

if __name__ == '__main__':
    main()


