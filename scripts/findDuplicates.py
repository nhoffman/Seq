#!/usr/bin/env python

import sys
import logging
from optparse import OptionParser
import pprint
import time

import Seq
from Seq.sequtil import split_and_merge

log = logging

def rlist(d, seqs, fout):

    """write an R-format list of character vectors"""

    fout.write('duplicates <- list(')
    items = iter(sorted(d.items()))
    parent, children = items.next()
    fout.write('\n   c(%s)' %
               (','.join('"%s"'%seqs[i].name for i in [parent]+children)))

    for parent, children in items:
        fout.write(',\n   c(%s)' %
                   (','.join('"%s"'%seqs[i].name for i in [parent]+children)))

    fout.write('\n)\n')


def main():

    usage = """%prog [options]

Read sequences in fasta format and identify a single sequence to
represent each set of substrings or identical sequences.
"""

    parser = OptionParser(usage=usage, version="$Id$")

    parser.set_defaults(
    infile=None,
    verbose=0,
    nchunks=0,
    chunksize=None,
    compare_type='contains',
    outfile=None,
    r_file=None
    )

    parser.add_option("-f", "--fasta-file", dest="infile",
        help='Input file containing sequences in fasta format',
        metavar='FILE')

    parser.add_option("-o", "--outfile", dest="outfile",
        help='Output file in fasta format',
        metavar='FILE')

    parser.add_option("-r", "--r-output", dest="r_file",
        help='Output file containing an R-language list of character vectors',
        metavar='FILE')

    parser.add_option('-n','--nchunks', dest='nchunks', metavar='INT', type='int', help='Number of partitions.')
    parser.add_option('-c','--chunksize', dest='chunksize', metavar='INT', type='int', help='Number of strings in each partition (overrides --nchunks).')
    parser.add_option('-t','--compare-type',dest='compare_type',metavar='VAL',type='choice',choices=['eq','contains'],
                      help='Type of comparison: "contains" (the default; finds longest sequences containing sets of substrings) or "eq" (selects single representatives from groups of identical sequences).')

    parser.add_option("-v", "--verbose",
        action="count", dest="verbose",
        help="increase verbosity of screen output (eg, -v is verbose, -vv is more so)")

    options, args = parser.parse_args()

    loglevel = {0:logging.WARNING,
                1:logging.INFO,
                2:logging.DEBUG}.get(options.verbose, logging.DEBUG)

    verbose_format = '%(levelname)s %(funcName)s %(lineno)s %(message)s'
    logformat = {0:'%(message)s',
        1:verbose_format,
        2:verbose_format}.get(options.verbose, verbose_format)

    if __debug__:
        logformat = verbose_format

    # set up logging
    logging.basicConfig(file=sys.stdout,
        format=logformat,
        level=loglevel)

    comp = options.compare_type

    infile = options.infile
    if not infile:
        log.error('Please provide an input file using -f/--fasta-file\n')
        parser.print_usage()
        sys.exit(1)

    seqs = Seq.io_fasta.read(open(infile).read(),
                             degap=True, style='upper')


    strings = tuple(seq.seq for seq in seqs)
    nstrings = len(strings)
    log.warning('Input contains %s items' % nstrings)

    start = time.time()

    if options.chunksize:
        chunksize = options.chunksize
    elif options.nchunks and options.nchunks > 1:
        chunksize = int(nstrings/options.nchunks) + 1
    else:
        chunksize = nstrings

    log.warning('chunksize = %s' % chunksize)

    d = split_and_merge(strings, comp, chunksize)

    log.warning('Input data can be represented by %s superstrings (%.2f%% of the input number)' % (len(d), 100*(len(d)/float(nstrings))))
    log.warning('grand total is %.2f secs' % (time.time()-start))

    if options.outfile:
        fout = open(options.outfile,'w')
        for parent, children in sorted(d.items()):
            s = seqs[parent]
            s.hea = ' '.join(seqs[c].name for c in children)
            fout.write(Seq.io_fasta.write(seqs[parent], hea=True))
        fout.close()

    if options.r_file:
        fout = open(options.r_file,'w')
        rlist(d, seqs, fout)
        fout.close()

if __name__ == '__main__':
    main()

