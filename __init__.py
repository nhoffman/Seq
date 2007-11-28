import os

__version__ = '$Id: __init__.py 1696 2007-11-22 01:07:16Z n.hoffman $'

__all__ = """
Dictionaries
Sequence
io_clustal
io_embl
io_fasta
io_phylip
io_uspto
sequtil
run_fasta
run_needle
run_clustalw
run_hmmer
""".split()

import Dictionaries
from Sequence import Seq
import io_clustal
import io_embl
import io_fasta
import io_phylip
import io_uspto
import sequtil
import run_fasta
import run_needle
import run_clustalw
import run_hmmer

class ExecutionError(Exception):
    pass