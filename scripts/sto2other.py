#!/usr/bin/env python

import sys
import Seq
from optparse import OptionParser

def main():

    usage = """%prog [options] infile.sto

Reads sequence alignment in stockholm format (eg, output of
Infernal cmalign) and prints fasta-format sequences to stdout."""

    parser = OptionParser(usage=usage, version="$Id$")
    parser_builtins = set(dir(parser))

    parser.set_defaults(
    keep_struct=False,
    keep_ref=False,
    case='upper',
    format='fasta',
    renum=None)

    parser.add_option("-f","--infile", dest='infile', metavar='FILE',
                     help='Input file')
    parser.add_option("-s", "--keep-struct", dest="keep_struct",
        help="keep structural model (SS_cons)", action='store_true')
    parser.add_option("-r", "--keep-ref", dest="keep_ref",
        help="keep structural model (SS_cons)", action='store_true')
    parser.add_option("-c", "--case", dest="case", type='choice',
                      choices=['upper','lower','input'],
                      help="change case of sequence text to upper case ('upper') lower case ('lower') or leave unchanged ('input')")
    parser.add_option("-F","--format", dest="format", type="choice", choices=["fasta","phylip","phylip_relaxed"],
                      metavar=[],help="Choose FORMAT for output file.")
    parser.add_option("-n","--numbers", dest="renum", metavar='FILE',
                      help="Replace names in output with s1, s2, s3...sN and write mapping of names to FILE (phylip format only).")
    parser.add_option('-R','--seq-range',dest='seq_range',metavar='x,y',
                      help='Restrict output to sequences in range x,y inclusive (1-index).')

    # TODO: add width argument, pass to io_fasta, io_phylip

    options, args = parser.parse_args()


    infile = options.infile

    if options.case == 'input':
        style=None
    else:
        style=options.case

    seqs = Seq.io_stockholm.read(open(infile).read(),
                                 case=options.case,
                                 keep_struct=options.keep_struct,
                                 keep_ref=options.keep_ref)

    # restrict to sequences in range if specified
    if options.seq_range:
        start,stop=options.seq_range.split(',')
        seqs = [seqs[i] for i in xrange(int(start)-1,int(stop))]

    if options.format == 'fasta':
        output = Seq.io_fasta.write(seqs)
    elif options.format == 'phylip':
        if options.renum:
            renumfile = open(options.renum,'w')
            renamer = Seq.io_phylip.renumber()
            for seq in seqs:
                renumfile.write('\t'.join([renamer.next(),seq.name])+'\n')
            renumfile.close()
            renum = True
        else:
            renum = False
        output = Seq.io_phylip.write(seqs, width=None, renum=renum)
    elif options.format == 'phylip_relaxed':
        output = '%s %s\n' % (len(seqs), len(seqs[0]))
        for seq in seqs:
            output += '%s %s\n' % (seq.name, seq.seq)
        
    sys.stdout.write(output)

if __name__ == '__main__':
    main()
