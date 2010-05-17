"""
I/O for phylip format sequences.
"""

__version__ = "$Id$"

import re, os, sys
from Seq import Seq
import textwrap
import itertools

def _toPhylip(seq, width=None, name=None):
    """Writes a string in sequential phylip format from a sequence
    object, seq.  name is used instead of seq.getName() if supplied.
    Mercilessly truncates names to 10 characters."""

    if name is None:
        name = seq.name

    output = '%-10s%s' % (name[:10], seq.seq)

    if width:
        output = textwrap.fill(output, width)

    return output

def read(*args, **kwargs):
    """
    Not implemented yet
    """
    raise AttributeError('io_phylip.read() is not implemented yet.')

def renumber():
    """
    Return a generator used to substitute s1, s2, ... sN for names.
    """

    counter = itertools.count(1)
    while True:
        yield 's%s'%counter.next()

def write(seqs, width=60, renum=False):
    """Creates a string representing a sequential phylip2 format
    sequence alignment from a list of sequences. If renum is True,
    sequentially renames sequences s1, s2 ... sN (useful for long
    names)."""

    # species, characters
    output = ['%s %s' % (len(seqs), len(seqs[0]))]

    if renum:
        renamer = renumber()
        output.extend(_toPhylip(s, width, renamer.next()) for s in seqs)
    else:
        output.extend(_toPhylip(s, width) for s in seqs)

    return '\n'.join(output) + '\n'

if __name__ == '__main__':
    test()

