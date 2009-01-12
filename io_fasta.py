"""
I/O for fasta sequence format.
"""

__version__ = "$Id$"

import re, os, sys
import warnings

from Seq import Seq
from sequtil import wrap, removeWhitespace, removeAllButAlpha

class FastaFormatError(Exception):
    pass

def read( strin, degap=False, style=None, preprocess=None):
    """
    * strin - one or more fasta format sequences. The first non-whitespace
    character must be >.
    * degap (bool) - if True, Non-alphanumeric characters are removed
    * style - None (no change to input), 'upper', or 'lower'
    * preprocess - None or a function accepting a single argument "seqstr"
      for modifying the input sequence string arbitrarily. If a function
      is provided, degap and style are ignored.
    """

    gt_count = strin.count('>')
    flist = strin.strip().split('>')
    # the folowing may come at the expense of a performance hit:
    # flist = re.split(r'^\s*>', strin.strip(), re.MULTILINE)

    seqlist = []
    for f in flist:

        if f.strip() == '':
            continue

        try:
            firstline, rawseq = f.strip().split('\n', 1)
        except ValueError:
            raise FastaFormatError, 'The input fasta sequence appears to be improperly formatted (characters 1-50):\n%s' % `f[:50]`

        try:
            name, header = firstline.split(None,1)
        except ValueError:
            name, header = firstline.strip(), ''

        if preprocess is None:
            if degap:
                seq = removeAllButAlpha(rawseq)
            else:
                seq = removeWhitespace(rawseq)

            if style == 'upper':
                seq = seq.upper()
            elif style == 'lower':
                seq = seq.lower()
        else:
            seq = preprocess(seq)

        seqlist.append(Seq(name, seq, header))

    #sanity check
    if gt_count != len(seqlist):
        msg = 'input string contained %s ">" characters but only %s sequences were found '
        raise FastaFormatError, msg % (gt_count, len(seqlist))

    return seqlist

def readFasta(strin, *args):

    raise Exception('This function is deprecated; use io_fasta.read instead.')

def write( seq_or_list, linelength=60, hea=True ):
    """Returns a fasta-formatted string given a single Seq object or
    list of objects. String always ends with a single trailing newline."""

    if type(seq_or_list) != type([]):
        seq_or_list = [seq_or_list]

    return ''.join([_write_fasta(seq, linelength, hea) for seq in seq_or_list])

def writeFasta( seq_or_list, *args ):

    raise Exception('This function is deprecated; use io_fasta.write instead.')

def _write_fasta( seq, linelength, hea ):

    output = ['>']
    output.append( seq.name )
    if hea and seq.hea:
        output.append( ' ' + seq.hea)
    output.append('\n')
    output.append( wrap(seq.seq, linelength) )

    return ''.join(output)
