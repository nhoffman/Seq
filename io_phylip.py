"""
I/O for phylip format sequences.
"""

__version__ = "$Id$"

import re, os, sys
from Seq import Seq
from sequtil import breakLines

okchar = re.compile(r"[\n\ _\-ACGTN\d]")
def _seqToPhylip( seq, name=None):
    """Writes a string in sequential phylip format from a sequence object, seq.
    name is used instead of seq.getName() if supplied.
    Mercilessly truncates names to 10 characters."""

    if name == None:
        name = seq.name

    str = '%-10s%s' % (name[:10], seq.seq)

    output = breakLines(str, 60)

    return output

def write( seqList ):
    """Creates a string representing a sequential phylip2 format sequence
    alignment from a list of sequences. If renum=1, sequentially
    renames sequences s1, s2 ... sN (useful for long names)."""

    output = []
    # species, characters
    output.append( '%s %s' % (len(seqList), len(seqList[0])) )

    for seq in seqList:
        output.append(_seqToPhylip(seq))
    output.append('\n')

    return '\n'.join(output)

def test():
    """Test routines in this module"""
    import glob, io_fasta

    #infiles = glob.glob('testfiles/*.fasta')
    infiles = glob.glob('/Users/nhoffman/blast2tree/Seq3/testfiles/*.fasta')

    for filename in infiles:
        instr = open(filename).read()
        seqlist = io_fasta.readFasta(instr)
        print write( seqlist )


if __name__ == '__main__':
    test()

