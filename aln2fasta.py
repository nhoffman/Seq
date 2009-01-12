#!/usr/local/bin/python

import io_clustal, io_fasta, sys

def main():

    infile = sys.argv[1]

    instr = open(infile).read()

    seqlist = io_clustal.readAlnStr(instr)

    print io_fasta.writeFasta( seqlist )



main()
