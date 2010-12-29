Package: Seq
============

This package contains many utilities for biological sequence
manipulation that I have accumulated over the years. The first thing
to point out is that there is much duplication of functionality
provided by the biopython project. If you need to parse various
sequence file formats (fasta, genbank, etc), you should probably go
there instead. However, there are a few goodies in here that I haven't
found elsewhere. Some highlights:

Sequence de-duplication::

  py> import Seq
  py> seqs = ('TATATA','TATATA', 'TATAT', 'AAGCAG', 'AAGC', 'TTTTT')
  py> print Seq.sequtil.coalesce(seqs)
  {0: [1, 2], 3: [4], 5: []} 

Dependencies
------------



Installation
------------

Uses the basic "setup.py" routine::

 sudo python setup.py install

