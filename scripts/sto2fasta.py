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
    case='upper')

    parser.add_option("-s", "--keep-struct", dest="keep_struct",
        help="keep structural model (SS_cons)", action='store_true')
    parser.add_option("-r", "--keep-ref", dest="keep_ref",
        help="keep structural model (SS_cons)", action='store_true')
    parser.add_option("-c", "--case", dest="case", type='choice',
                      choices=['upper','lower','input'],
                      help="change case of sequence text to upper case ('upper') lower case ('lower') or leave unchanged ('input')")

    options, args = parser.parse_args()

    try:
        infile = args[0]
    except IndexError:
        print dir(parser)
        parser.print_usage()
        sys.exit()

    if options.case == 'input':
        style=None
    else:
        style=options.case

    seqlist = Seq.io_stockholm.read(open(infile).read(),
                                    case=options.case,
                                    keep_struct=options.keep_struct,
                                    keep_ref=options.keep_ref)
    print Seq.io_fasta.write( seqlist )

if __name__ == '__main__':
    main()
