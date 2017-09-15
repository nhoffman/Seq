Package: Seq
============

**This project is deprecated - I'm leaving it here because some very old projects depend on it, but please don't use this for anything new!**

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

Multiple alignment formatting::

 % alnview.py --help
 Usage: alnview.py [options]

 Create formatted sequence alignments with optional pdf output.


 Options:
   --version             show program's version number and exit
   -h, --help            show this help message and exit
   -f INFILE, --infile=INFILE
			 input FILE containing sequence alignment
   -o OUTFILE, --outfile=OUTFILE
			 Write output to a pdf file.
   -c, --add_consensus   Include show a consensus sequence [False]
   -d COMPARE_TO, --compare-to=COMPARE_TO
			  Number of the sequence to use as a reference.
			 Nucleotide positions identical to the reference will
			 be shown as a '.' The default behavior is to use the
			 consensus sequence as a reference. Use the -i option
			 to display the sequence numbers for reference. A value
			 of -1 suppresses this behavior.
   -i, --number-sequences
			 Show sequence number to left of name. [False]
   -x, --exclude-invariant
			 only show columns with at least min_subs non-consensus
			 bases (set min_subs using the -s option) [False]
   -g, --exclude-gapcols
			 Remove columns containing only gap characters. [False]
   -s NUMBER, --min_subs=NUMBER
			 minimum NUMBER of substitutions required to define a
			 position as variable. [1]
   -n NUMBER, --name-max=NUMBER
			 maximum width of sequence name. [35]
   -w NUMBER, --width=NUMBER
			 Width of sequence to display in each block in
			 characters [115]
   -F NUMBER, --fontsize=NUMBER
			 Font size for pdf output [7]
   -C CASE, --case=CASE  Convert all characters to a uniform case
			 ('upper','lower') [none]
   -p NUMBER, --per-page=NUMBER
			 Sequences (lines) per page of pdf output. [75]
   -r RANGE, --range=RANGE
			 Range of aligned positions to display (eg '-r
			 start,stop')
   -O ORIENTATION, --orientation=ORIENTATION
			 Choose from portrait or landscape. [portrait]
   -b NUMBER, --blocks-per-page=NUMBER
			 Number of aligned blocks of sequence per page [1]
   -q, --quiet           Suppress output of alignment to screen. [False]
   -v, --verbose         increase verbosity of screen output (eg, -v is
			 verbose, -vv is more so)

Dependencies
------------

 * python 2.6+
 * ReportLab (http://www.reportlab.com/software/opensource/) - for pdf-format multiple alignments.
 * various freely-available bioinformatics tools (if you want to use
   any of the run_* methods), eg clustalw, hmmer, fasta3*, infernal

Installation
------------

Uses the basic "setup.py" routine::

 sudo python setup.py install

