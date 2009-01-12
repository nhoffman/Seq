"""
I/O for clustalw aln format sequences.
Public methods are:
read
readAlnStr (deprecated)
"""

__version__ = "$Id$"

import os
import sys
import logging

log = logging

import Seq

def read(instr):
    """Input is a clustalw .aln file; returns a list of Seq objects"""

    data = {}
    namelist = []
    lines = instr.splitlines()
    lines.pop(0) # first line reads CLUSTAL W (1.81) multiple sequence alignment
    for line in lines:
        if line.strip() == '' or line.find('**') != -1 or len(line.split()) != 2:
            continue

        name, seqline = line.split(None,1)
        #print '|%s|\n|%s|' % (name,seq)

        # maintain ordered list of names
        if not data.has_key(name):
            namelist.append(name)
        data[name] = data.get(name,[]) + [seqline]


    seqlist = []
    for name in namelist:
        seq = Seq.Seq(name=name, seq=''.join(data[name]))
        seqlist.append(seq)

    return seqlist

# for backward compatibility
def readAlnStr(instr):
    log.info('io_clustal.readAln is deprecated: use io_clustal.read instead')
    return read(instr)
