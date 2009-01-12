#!/usr/bin/env python

import sys
import Seq

def main():
    """
    Usage: aln2fasta.py infile.aln

    Reads sequence alignment in clustalw output .aln format 
    and prints fasta-format sequences to stdout.
    """

    try:
        infile = sys.argv[1]
    except IndexError:
        print main.__doc__
        sys.exit(1)
        
    seqlist = Seq.io_clustal.read(open(infile).read())
    print Seq.io_fasta.write( seqlist )

if __name__ == '__main__':
    main()
