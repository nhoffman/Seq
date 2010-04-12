import sys

__version__ = '0.1.'+'$Rev$ 0'.split()[1]
__version_info__ = tuple([ int(num) for num in __version__.split('.')])

_min_python_version = '2.5.0'

def _check_python_version():
    vsplit = lambda x: tuple([int(n) for n in x.split('.')])
    sys_version = sys.version.split()[0]
    version = vsplit(sys_version)
    if version < vsplit(_min_python_version):
        raise SystemError('sqtools requires Python version %s or greater (current version is %s)' % \
                          (_min_python_version, sys_version))

_check_python_version()

__all__ = """
Dictionaries
Sequence
io_clustal
io_embl
io_fasta
io_phylip
io_uspto
io_rdp
import io_stockholm
sequtil
run_fasta
run_needle
run_clustalw
run_hmmer
import run_infernal
""".split()

import Dictionaries
from Sequence import Seq
import io_clustal
import io_embl
import io_fasta
import io_phylip
import io_uspto
import io_rdp
import io_stockholm
import io_genbank
import sequtil
import run_fasta
import run_needle
import run_clustalw
import run_hmmer
import run_infernal

from sequtil import find_exec

class ExecutionError(Exception):
    pass
