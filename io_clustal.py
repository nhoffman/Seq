"""
I/O for clustalw aln format sequences.
Public methods are:
readAlnStr
"""

__version__ = "$Id: io_clustal.py 1487 2007-10-10 17:42:39Z n.hoffman $"

import re, os, sys
from Seq import Seq

def readAlnStr(instr):
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
		seq = Seq(name=name, seq=''.join(data[name]))
		seqlist.append(seq)
	
	return seqlist
			
def test():
	"""Test routines in this module"""
	import glob
	mdir,_ = os.path.split(__file__)
	infiles = glob.glob(os.path.join(mdir,'testfiles/*.aln'))
	
	for filename in infiles:
		instr = open(filename).read()
		seqlist = readAlnStr(instr)
		print 'found %s sequences in %s' % (len(seqlist), filename)
		for seq in seqlist:
			print '%15s' % seq.name, len(seq), seq[:10],'...',seq[-10:]
		
if __name__ == '__main__':
	test()
	
