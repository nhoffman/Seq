#!/usr/local/bin/python

"""Test components of the Seq package"""

import sys, os

from Seq import *
from Seq.sequtil import translate, reverse, complement, reverse_complement

Seq = Sequence

def tell(expression, g, l):
	print '*   print %s \n%s\n%s' % (expression, eval(expression, g, l),'-'*40 )

def seq_class_test():
	"""test Seq class"""
	
	s = 'AGAGAGAGAGCTCTCTCTCT---~~~....GTGTGTGTGT' * 3
	
	seq = Seq.Seq(name='name1', seq=s, hea='some random header')
		
	g, l = globals(), locals()
	for e in [ \
	'`seq`',
	'seq',
	'str(seq)',
	"seq == 'AGAGAGAGAGCTCTCTCTCT---~~~....GTGTGTGTGT'*3",
	"seq == 'blehblah'",
	'seq()',
	'len( seq )',
	'seq[0:10]',
	'seq[0:-1]',
	'seq[-1], seq[-2]',
	'seq.getSeq1(1,11)',
	'"ct" in seq',
	'"cg" in seq',
	'" ".join([i for i in seq])'
	]:
		tell(e, g, l)

def basic_seq_manipulation_test():

	s = """agcaccaacacacacaaacccaaccaagcacatagtaacatcgaccgatcggcat
ggcgcacttccaggaggtggactactgctcggaggaggtgagggcggtgggcaac
ccggcccgccgcggcggcggcgtgcaggagcacatcgtcaaggagacgttcgtgc
aggagttcgacacctccggccgccgccacggtcaccacggtcaccacggccgcgg
ctctggtcacttcgaggtgcgcgagagcaggctcgaggaggacttcaacacccgc
accggggagttccacgagcgcaaggagaacttcgtcgtcagggccgatgactgag
cttacacgtaacggagcacactacgatgtgtgtatatgtatgcatgtcagcagta
tatgtatgtgtgatgttgcgcacagtcgtatagcgtatgcaggcgtgcgtg"""

	s2 = """agcaccaacacacacaaacccaaccaagcacatagtaacatcgaccgatcggcat
ggcgcacttccaggag...gactactgct~ggaggaggtgagggcggtgggcaac
ccg1cccgccgcggcggc--gcgtgcaggagcacatcgtcaaggagacgttcgtgc
aggagttcgacacbctccgg"""

	s = ''.join(s.split())
	s2 = ''.join(s2.split())
	
	seq = Seq.Seq(name='seq1', seq=s, hea='spam')

	g, l = globals(), locals()
	for e in [ \
	'`seq`',
	'`translate(seq)`',
	'`translate(s)`',
	'`translate(seq.seq)`',
	'`s2`',
	'`translate(s2)`',
	'translate(seq)',
	'translate(seq[:])',
	'translate(seq.seq)',
	'reverse(seq[:])',
	'complement(seq[:])',
	'reverse_complement(seq[:])'
	]:
		tell(e, g, l)
	
def main():
	
	seq_class_test()
	basic_seq_manipulation_test()
	io_embl.test()
	io_uspto.test()
	io_fasta.test()
	io_clustal.test()
	sequtil.test()

if __name__ == '__main__':
	main()
