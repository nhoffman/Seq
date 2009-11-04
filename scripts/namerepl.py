#!/usr/bin/env python

import sys
import Seq
from optparse import OptionParser
import re

def main():

    usage = """%prog [options]

Replace strings (eg, sequence names) in a file based on the provided mapping.
"""

    parser = OptionParser(usage=usage, version="$Id: dan.py 3035 2008-12-19 23:30:39Z nhoffman $")
    parser_builtins = set(dir(parser))

    parser.set_defaults(
        infile=None,
        mapfile=None,
        outfile=None)

    parser.add_option("-f","--infile", dest='infile', metavar='FILE',
                     help='Input file (target of string replacement)')
    parser.add_option("-m","--mapfile", dest='mapfile', metavar='FILE',
                     help='File providing the mapping for string replacement.')
    parser.add_option("-o","--outfile", dest='outfile', metavar='FILE',
                     help='Output file (writes to stdout if not provided)')
        
    options, args = parser.parse_args()

    infile = options.infile
    mapfile = options.mapfile

    if options.outfile:
        fout = open(options.outfile,'w')
    else:
        fout = sys.stdout
    
    mapping = dict([line.split() for line in open(mapfile) if line.strip()])

    replaced = re.sub(r'\bs\d+\b',
                      lambda match: mapping.get(match.group(0), match.group(0)),
                      open(infile).read())

    fout.write(replaced)
    
if __name__ == '__main__':
    main()
