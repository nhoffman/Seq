"""
I/O for genbank sequence format. The read method is extremely fragile
and was written for a very narrow set of purposes - much better to
extract information from Genbank's XML-format!

see http://www.ncbi.nlm.nih.gov/projects/collab/FT/
"""

__version__ = "$Id$"

import re, os, sys
import warnings
import logging
from collections import defaultdict
import pprint

log = logging

from Seq import Seq
from sequtil import wrap, removeWhitespace, removeAllButAlpha

class gbSeq(Seq):
    """
    Provides some convenience attributes for accessing data in
    Seq.data
    """

    def __init__(self, *args, **kwargs):
        super(gbSeq, self).__init__(*args, **kwargs)
        self.locus = self.data['LOCUS'][0]
        self.taxid = self.data['FEATURES'][1]['source'][1]['db_xref'][0].split(':')[1]
        self.organism = self.data['FEATURES'][1]['source'][1]['organism'][0]

def read(input,
         namefun=lambda d: d['ACCESSION'][0].split()[0],
         keep_origin=False):
    """
    * input - filename or a string containing Genbank format sequence records
    * namefun - a function that operates on the dict contained in the data attribute
      (see below) to generate a string to be used as the sequence name.
    * keep_origin - if True, retains 'ORIGIN' element in data (the raw sequence string)

    return a generator of gbSeq objects, with sequence name set
    according to 'namefun'. The data attribute of each seq object
    contains all of the data from the genbank record represented as
    nested dicts and tuples::

     {'ACCESSION': ('AB512777', {}),
      'AUTHORS': ('Watanabe,K., Chao,S.-H., Sasamoto,M., Kudo,Y. and Fujimoto,J.',
                  {}),
      'AUTHORS-1': ('Watanabe,K., Chao,S.-H. and Fujimoto,J.', {}),
      'DEFINITION': ('Lactobacillus hammesii gene for 16S rRNA, partial sequence, strain: YIT 12110.',
                     {}),
      'FEATURES': ('Location/Qualifiers',
                   {'rRNA': ('<1..>1553', {'product': ('16S ribosomal RNA', {})}),
                    'source': ('1..1553',
                               {'db_xref': ('taxon:267633', {}),
                                'mol_type': ('genomic DNA', {}),
                                'note': ('type strain of Lactobacillus hammesii',
                                         {}),
                                'organism': ('Lactobacillus hammesii', {}),
                                'strain': ('YIT 12110', {})})}),
      'JOURNAL': ('Unpublished', {}),
      'JOURNAL-1': ('Submitted (15-JUL-2009) Contact:Koichi Watanabe Yakult Central Institute for Microbiological Research, Culture Collection and Microbial Systematics; 1796 Yaho, Kunitachi, Tokyo 186-8650, Japan',
                    {}),
      'KEYWORDS': ('.', {}),
      'LOCUS': ('AB512777                1553 bp    DNA     linear   BCT 17-SEP-2009',
                {}),
      'ORGANISM': ('Lactobacillus hammesii Bacteria; Firmicutes; Lactobacillales; Lactobacillaceae; Lactobacillus.',
                   {}),
      'REFERENCE': ('1', {}),
      'REFERENCE-1': ('2  (bases 1 to 1553)', {}),
      'SOURCE': ('Lactobacillus hammesii', {}),
      'TITLE': ('Novel Lactobacillus species isolated from stinky tofu brine', {}),
      'TITLE-1': ('Direct Submission', {}),
      'VERSION': ('AB512777.1  GI:258612363', {})}
    """

    seqdelim = r'//'
    leadingblank = ' '*10

    if input.find('\n') == -1 and os.access(input, os.F_OK):
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
                k,v = line[1:].split('=',1)
                addto.append([k,v.strip('"')])
            else:
                addto.append(line)
        else:
            try:
                key, val = line.split(None,1)
            except ValueError:
                key, val = line, ''

            if line.strip() == seqdelim:
                d = _as_dict(record)
                seqstr = removeAllButAlpha(d['ORIGIN'][0])
                if not keep_origin:
                    del d['ORIGIN']
                yield gbSeq(name=namefun(d), seq=seqstr, data=d)

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





