#!/usr/bin/env python

import sys
import logging
import collections
from optparse import OptionParser
import pprint
import time
from itertools import izip, chain, repeat, islice, takewhile
import cProfile
import pstats
import operator

import Seq

try:
    import pp
except ImportError:
    pp_ok = False
else:
    pp_ok = True

log = logging

# try:
#     import psyco
# except ImportError:
#     log.error('could not import psyco')
#     pass

# izip_longest is new in Python 2.6, provide replacement for Python 2.5
try:
    from itertools import izip_longest
except ImportError:
    def izip_longest(*args, **kwds):
        # see http://docs.python.org/library/itertools.html#recipes
        # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
        fillvalue = kwds.get('fillvalue')
        def sentinel(counter = ([fillvalue]*(len(args)-1)).pop):
            yield counter()         # yields the fillvalue, or raises IndexError
        fillers = repeat(fillvalue)
        iters = [chain(it, sentinel(), fillers) for it in args]
        try:
            for tup in izip(*iters):
                yield tup
        except IndexError:
            pass

def grouper(n, iterable, pad=True):
    """
    Return sequence of n-tuples composed of successive elements
    of iterable; last tuple is padded with None if necessary. Not safe
    for iterables with None elements.
    """

    args = [iter(iterable)] * n
    iterout = izip_longest(fillvalue=None, *args)

    if pad:
        return iterout
    else:
        return (takewhile(lambda x: x is not None, c) for c in iterout)

def flatten(d):
    return sorted(d.keys() + list(chain(*d.values())))

#### the real work is done in coalesce and merge

def coalesce(strings, idx=None, comp='contains', log=log):

    """
    Groups a collection of strings by identifying the longest string
    representing each nested set of substrings (if comp='contains') or
    into sets of identical strings (if comp='eq')

    Input
    =====

     * strings - a tuple of N strings
     * idx - an optional sequence of integer indices into strings; if missing,
       will include all elements in strings.

     Output
     ======

     * a dict keyed by indices in strings. Each key i returns a list of
       indices corresponding to strings nested within (or identical to) the
       string at strings[i].
    """

    start = time.time()

    if idx:
        idx = list(idx)
    else:
        idx = range(len(strings))

    if __debug__:
        idx_orig = idx[:]

    # sort idx by length, descending
    idx.sort(key=lambda i: len(strings[i]),reverse=True)
    log.debug('sort completed at %s secs' % (time.time()-start))
    nstrings = len(idx)

    #d = collections.defaultdict(list, ((i,list()) for i in idx))
    d = dict((i,list()) for i in idx)

    # operator.eq(a,b) <==> a == b
    # operator.contains(a,b) <==> b in a
    compfun = getattr(operator, comp)

    cycle = 0
    while len(idx) > 0:
        parent_i = idx.pop(0)
        parent_str = strings[parent_i]
        if __debug__: # suppress using python -O
            cycle += 1
            log.debug('cycle %3s, %3s remaining, parent length=%4s' % \
                (cycle, len(idx), len(strings[parent_i])))

        for i, child_i in enumerate(idx):
            # if strings[child_i] in parent_str:
            if compfun(parent_str,strings[child_i]):
                # assert child_i == idx.pop(i)
                d[parent_i].append(idx.pop(i))
                del d[child_i]

        if __debug__:
            log.debug("i=%-5s len(parent)=%3s children:%s" % \
                (parent_i, len(strings[parent_i]), d.get(parent_i, 'no children')))

    log.warning('Coalesce %s strings to %s in %.2f secs' % (nstrings, len(d), time.time()-start))

    if __debug__:
        dFlat = flatten(d)
        log.info('checking d of length %s with min,max=%s,%s' % \
            (len(d), min(dFlat), max(dFlat)))

        assert set(idx_orig) == set(dFlat)

        for parent, children in d.items():
            for child in children:
                assert strings[child] in strings[parent]

    return d

def merge(strings, d1, d2=None, comp='contains'):

    """
    Merge two dictionaries mapping superstrings to substrings.

    Input
    =====

     * strings - a tuple of N strings
     * d1, d2 - output of coalesce()
     * comp - type of string comparison, passed to coalesce ("contains" or "eq")

    Output
    ======

     * a single dict mapping superstrings to substrings

    """

    if d2 is None:
        log.warning('d2 not provided, returning d1')
        return d1

    d = coalesce(strings, idx=d1.keys()+d2.keys(), comp=comp)

    for i, dvals in d.items():
        if dvals:
            d[i].extend(list(chain(*[d1.get(j,[]) for j in dvals])))
            d[i].extend(list(chain(*[d2.get(j,[]) for j in dvals])))
        d[i].extend(d1.get(i,[]))
        d[i].extend(d2.get(i,[]))

    if __debug__:
        d1Flat, d2Flat, dFlat = flatten(d1), flatten(d2), flatten(d)
        log.info('checking d of length %s with min,max=%s,%s' % \
            (len(d),min(dFlat),max(dFlat)))

        assert set(d1Flat + d2Flat) == set(dFlat)

        for parent, children in d.items():
            for child in children:
                assert strings[child] in strings[parent]


    return d

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

findDuplicates -h prints options"""

    parser = OptionParser(usage=usage, version="$Id: dan.py 3035 2008-12-19 23:30:39Z nhoffman $")

    parser.set_defaults(
    infile=None,
    verbose=0,
    nchunks=4,
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

    seqs = Seq.io_fasta.read(open(options.infile).read(),
                             degap=True, style='upper')

    strings = tuple(seq.seq for seq in seqs)
    nstrings = len(strings)
    log.warning('Input contains %s items' % nstrings)

    start = time.time()

    if options.chunksize:
        chunksize = options.chunksize
    else:
        chunksize = int(nstrings/options.nchunks) + 1

    log.warning('chunksize = %s' % chunksize)

    ### the important stuff happens from here...
    chunks = grouper(n=chunksize, iterable=xrange(nstrings), pad=False)
    # TODO: parallelize me
    coalesced = [coalesce(strings, c, comp=comp) for c in chunks]

    cycle = 1
    while len(coalesced) > 1:
        log.warning('merge cycle %s, %s chunks' % (cycle,len(coalesced)))
        # TODO: parallelize me
        coalesced = [merge(strings, d1, d2, comp=comp) for d1,d2 in grouper(n=2, iterable=coalesced)]
        cycle += 1

    d = coalesced[0]
    ### ... to here

    assert set(flatten(d)) == set(range(nstrings))

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

