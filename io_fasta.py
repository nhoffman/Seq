"""
I/O for fasta sequence format.
Public methods:
readFasta
writeFasta
"""

__version__ = "$Id: io_fasta.py 1557 2007-10-25 00:20:58Z n.hoffman $"

import re, os, sys
import warnings

from Seq import Seq
from sequtil import wrap, removeWhitespace, removeAllButAlpha

class FastaFormatError(Exception):
    pass

def read( strin, degap=False, style=None):
    """strin is one or more fasta format sequences. The first non-whitespace
    character must be >. Non-alphanumeric characters are removed if degap is True. Choose a value of style from among None (no change to input), 'upper', and 'lower'"""
    
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
        
        if degap:
            seq = removeAllButAlpha(rawseq)
        else:
            seq = removeWhitespace(rawseq)
            
        if style == 'upper':
            seq = seq.upper()
        elif style == 'lower':
            seq = seq.lower()
            
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
    if hea:
        output.append( ' ' + seq.hea )
    output.append('\n')
    output.append( wrap(seq.seq, linelength) )
    
    return ''.join(output)
    
def test():
    """Test routines in this module"""
        
    import glob 
    #need to fix MANIFEST file to install testfiles at the below location
    #mdir,_ = os.path.split(__file__)
    #infiles = glob.glob(os.path.join(mdir,'testfiles/*.fasta'))
    infiles = glob.glob('testfiles/*.fasta')
    
    #print mdir
    print infiles
    
    seqlist = []
    for file in infiles:
        s = open(file).read()
        seqlist += read(s)
        
    print write( seqlist[0] )
    print write( seqlist[0], hea=False )
    print write( seqlist[1:] )

    
    
    
