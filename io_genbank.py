"""
I/O for genbank sequence format. The read method is extremely fragile
and was written for a very narrow set of purposes - much better to
extract information from Genbank's XML-format!

see http://www.ncbi.nlm.nih.gov/projects/collab/FT/
"""

__version__ = "$Id: io_stockholm.py 3189 2009-08-13 23:57:03Z nhoffman $"

import re, os, sys
import warnings
import logging
from collections import defaultdict
import pprint

log = logging

from Seq import Seq
from sequtil import wrap, removeWhitespace, removeAllButAlpha

def read(input, name='ACCESSION'):
    """
    * input - filename or a string containing stockholm format sequence alignment
    * case - specify "upper" or "lower" to force sequences into either

    return a generator of Seq objects, with sequence name set according to 'name'
    """
    
    seqdelim = r'//'
    leadingblank = ' '*10
    
    if len(input) < 50 and os.access(input, os.F_OK):
        lines = open(input)
    else:
        lines = input.splitlines()
    
    record = []
    addto = None
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        
        if line.startswith(leadingblank):
            line = line.strip()
            if line.startswith(r'/'):
                k,v = line[1:].split('=')
                addto.append([k,v.strip('"')])
            else:
                addto.append(line)
        else:
            try:
                key, val = line.split(None,1)
            except ValueError:        
                key, val = line, ''

            if line.strip() == seqdelim:
                thisdict = _as_dict(record)
                yield _as_seq(thisdict, name)
                record = []
                
            if key.isupper():
                record.append([])
                addto = record[-1]
            elif key[0].islower():
                record[-1].append([])
                addto = record[-1][-1]
            
            addto.extend([key, val])
            
def _as_dict(record):
    keycount = defaultdict(int)
    d = {}
    for x in record:
        k = x[0]
        vals = x[1:]
       
        # recursively convert lists of lists to dicts keyed by first element of each
        val = (' '.join([e for e in vals if isinstance(e,str)]),
            _as_dict([e for e in vals if isinstance(e,list)]))
                
        if k in keycount:            
            d['%s-%s' % (k,keycount[k])] = val
        else:            
            d[k] = val
        keycount[k] += 1    
            
    return d

def _as_seq(d, nametag):
    name = d[nametag][0]
    seq = removeAllButAlpha(d['ORIGIN'][0])
   
    return Seq(name, seq, data=d)
    
    


