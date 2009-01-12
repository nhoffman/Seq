"""
I/O for fasta sequence format variant generated by RDP aligner.
http://pyro.cme.msu.edu/pyro/aligner.jsp
"""

__version__ = "$Id$"

import re, os, sys
import warnings

from Seq import Seq
from sequtil import wrap, removeWhitespace, removeAllButAlpha

class FastaFormatError(Exception):
    pass

def read( strin, degap=False, style=None):
    """
    * strin - one or more fasta format sequences. The first non-whitespace
    character must be >.
    * degap (bool) - if True, Non-alphanumeric characters are removed
    """

    assert strin.startswith('>')
    flist = strin[1:].split('\n>')

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

        seq = re.sub(r'[^a-zA-Z-]','-',rawseq)

        if degap:
            seq = removeAllButAlpha(rawseq)

        if style == 'upper':
            seq = seq.upper()
        elif style == 'lower':
            seq = seq.lower()

        seqlist.append(Seq(name, seq, header))

    return seqlist


