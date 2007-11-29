"""
Contains various dictionaries for translation, encoding, etc. of nucleotide and amino acid sequences.
"""

__version__ = '$Id$'

translationWithoutAmbiguity = {'TAG': '*', 'TGG': 'W', 'CAG': 'Q', 'CCG': 'P', 'CGT': 'R', 'CTC': 'L',
'CTT': 'L', 'CGC': 'R', 'GCT': 'A', 'GTT': 'V', 'AAG': 'K', 'AAT': 'N', 'GTG': 'V',
'GCG': 'A', 'GTC': 'V', 'GCC': 'A', 'GTA': 'V', 'GCA': 'A', 'TCA': 'S', 'GAA': 'E',
'TCC': 'S', 'GAC': 'D', 'TTA': 'L', 'TCG': 'S', 'TTC': 'F', 'TAC': 'Y', 'GGC': 'G',
'TAA': '*', 'GGA': 'G', 'TGA': '*', 'GGG': 'G', 'TGC': 'C', 'TTT': 'F', 'CGG': 'R',
'GAT': 'D', 'TCT': 'S', 'GAG': 'E', 'CGA': 'R', 'TGT': 'C', 'GGT': 'G', 'TAT': 'Y', 
'CCC': 'P', '...': '.', 'CCA': 'P', 'AGT': 'S', 'CAA': 'Q', 'CAC': 'H', 'ACT': 'T', 
'CTA': 'L', 'CTG': 'L', 'ATT': 'I', 'TTG': 'L', 'AAA': 'K', 'CAT': 'H', 'AGA': 'R', 
'AGC': 'S', 'CCT': 'P', 'AGG': 'R', 'ATA': 'I', 'AAC': 'N', 'ATC': 'I', 'ACG': 'T', 
'ACA': 'T', 'ATG': 'M', 'ACC': 'T', '---': '-', '...': '-', '~~~': '-' }


translationWithAmbiguity = {'AAA':'K', 'AAC':'N', 'AAG':'K', 'AAR':'K', 'AAT':'N', 'AAY':'N', 'ACA':'T', 'ACB':'T', 
'ACC':'T', 'ACD':'T', 'ACG':'T', 'ACH':'T', 'ACK':'T', 'ACM':'T', 'ACN':'T', 'ACR':'T', 
'ACS':'T', 'ACT':'T', 'ACV':'T', 'ACW':'T', 'ACY':'T', 'AGA':'R', 'AGC':'S', 'AGG':'R', 
'AGR':'R', 'AGT':'S', 'AGY':'S', 'ATA':'I', 'ATC':'I', 'ATG':'M', 'ATH':'I', 'ATM':'I', 
'ATT':'I', 'ATW':'I', 'ATY':'I', 'CAA':'Q', 'CAC':'H', 'CAG':'Q', 'CAR':'Q', 'CAT':'H', 
'CAY':'H', 'CCA':'P', 'CCB':'P', 'CCC':'P', 'CCD':'P', 'CCG':'P', 'CCH':'P', 'CCK':'P', 
'CCM':'P', 'CCN':'P', 'CCR':'P', 'CCS':'P', 'CCT':'P', 'CCV':'P', 'CCW':'P', 'CCY':'P', 
'CGA':'R', 'CGB':'R', 'CGC':'R', 'CGD':'R', 'CGG':'R', 'CGH':'R', 'CGK':'R', 'CGM':'R', 
'CGN':'R', 'CGR':'R', 'CGS':'R', 'CGT':'R', 'CGV':'R', 'CGW':'R', 'CGY':'R', 'CTA':'L', 
'CTB':'L', 'CTC':'L', 'CTD':'L', 'CTG':'L', 'CTH':'L', 'CTK':'L', 'CTM':'L', 'CTN':'L', 
'CTR':'L', 'CTS':'L', 'CTT':'L', 'CTV':'L', 'CTW':'L', 'CTY':'L', 'GAA':'E', 'GAC':'D', 
'GAG':'E', 'GAR':'E', 'GAT':'D', 'GAY':'D', 'GCA':'A', 'GCB':'A', 'GCC':'A', 'GCD':'A', 
'GCG':'A', 'GCH':'A', 'GCK':'A', 'GCM':'A', 'GCN':'A', 'GCR':'A', 'GCS':'A', 'GCT':'A', 
'GCV':'A', 'GCW':'A', 'GCY':'A', 'GGA':'G', 'GGB':'G', 'GGC':'G', 'GGD':'G', 'GGG':'G', 
'GGH':'G', 'GGK':'G', 'GGM':'G', 'GGN':'G', 'GGR':'G', 'GGS':'G', 'GGT':'G', 'GGV':'G', 
'GGW':'G', 'GGY':'G', 'GTA':'V', 'GTB':'V', 'GTC':'V', 'GTD':'V', 'GTG':'V', 'GTH':'V', 
'GTK':'V', 'GTM':'V', 'GTN':'V', 'GTR':'V', 'GTS':'V', 'GTT':'V', 'GTV':'V', 'GTW':'V', 
'GTY':'V', 'MGA':'R', 'MGG':'R', 'MGR':'R', 'TAA':'*', 'TAC':'Y', 'TAG':'*', 'TAR':'*', 
'TAT':'Y', 'TAY':'Y', 'TCA':'S', 'TCB':'S', 'TCC':'S', 'TCD':'S', 'TCG':'S', 'TCH':'S', 
'TCK':'S', 'TCM':'S', 'TCN':'S', 'TCR':'S', 'TCS':'S', 'TCT':'S', 'TCV':'S', 'TCW':'S', 
'TCY':'S', 'TGA':'*', 'TGC':'C', 'TGG':'W', 'TGT':'C', 'TGY':'C', 'TRA':'*', 'TTA':'L', 
'TTC':'F', 'TTG':'L', 'TTR':'L', 'TTT':'F', 'TTY':'F', 'YTA':'L', 'YTG':'L', 'YTR':'L',
'---': '-', '...': '-', '~~~': '-'}

translationWithoutAmbiguity3 = {'CTT': 'Leu', 'ACC': 'Thr', 'AAG': 'Lys', 'AAA': 'Lys', 'ATC': 'Ile', 'AAC': 'Asn', 'ATA': 'Ile', 'AGG': 'Arg', 'CCT': 'Pro', 'CTC': 'Leu', 'AGC': 'Ser', 'ACA': 'Thr', 'AGA': 'Arg', 'CAT': 'His', '---': '---', 'AAT': 'Asn', 'ATT': 'Ile', 'CTG': 'Leu', 'CTA': 'Leu', 'ACT': 'Thr', 'CAC': 'His', 'ACG': 'Thr', 'CCG': 'Pro', 'AGT': 'Ser', 'CAG': 'Gln', 'CAA': 'Gln', 'CCC': 'Pro', 'TAT': 'Tyr', 'GGT': 'Gly', 'TGT': 'Cys', 'CGA': 'Arg', 'CCA': 'Pro', 'TCT': 'Ser', 'GAT': 'Asp', 'CGG': 'Arg', 'TTT': 'Phe', 'TGC': 'Cys', 'GGG': 'Gly', 'TAG': '***', 'GGA': 'Gly', 'TGG': 'Trp', 'GGC': 'Gly', 'TAC': 'Tyr', 'GAG': 'Glu', 'TCG': 'Ser', 'TTA': 'Leu', 'GAC': 'Asp', 'CGT': 'Arg', 'GAA': 'Glu', 'TAA': '***', 'GCA': 'Ala', '...': '---', 'GCC': 'Ala', 'GTC': 'Val', 'GCG': 'Ala', 'GTG': 'Val', 'TTC': 'Phe', 'GTT': 'Val', 'GCT': 'Ala', 'GTA': 'Val', 'TGA': '***', 'TTG': 'Leu', 'TCC': 'Ser', '~~~': '---', 'TCA': 'Ser', 'ATG': 'Met', 'CGC': 'Arg'}

translationWithAmbiguity3 = {'ACC': 'Thr', 'GAT': 'Asp', 'CCY': 'Pro', 'ACB': 'Thr', 'AGG': 'Arg', 'CCT': 'Pro', 'CCW': 'Pro', 'CCV': 'Pro', 'AGC': 'Ser', 'GCM': 'Ala', 'AGA': 'Arg', 'CCR': 'Pro', 'CCM': 'Pro', 'CCN': 'Pro', 'CCH': 'Pro', 'AGY': 'Ser', 'CCD': 'Pro', 'CCG': 'Pro', 'AGT': 'Ser', 'CCA': 'Pro', 'AGR': 'Arg', 'CCC': 'Pro', 'CCB': 'Pro', 'TAT': 'Tyr', 'TAR': '***', 'ACD': 'Thr', 'TAY': 'Tyr', 'TAG': '***', 'TAA': '***', 'TAC': 'Tyr', '...': '---', 'ATM': 'Ile', 'CTY': 'Leu', 'CCS': 'Pro', 'TTA': 'Leu', 'ACS': 'Thr', 'ACM': 'Thr', 'ATW': 'Ile', 'TTG': 'Leu', 'ACV': 'Thr', 'CCK': 'Pro', 'ACT': 'Thr', 'CTN': 'Leu', 'TTY': 'Phe', 'TCY': 'Ser', 'TCV': 'Ser', 'TCW': 'Ser', 'TCT': 'Ser', 'TCR': 'Ser', 'TCS': 'Ser', 'TTT': 'Phe', 'TCN': 'Ser', 'TCM': 'Ser', 'TCK': 'Ser', 'TCH': 'Ser', 'TTC': 'Phe', 'TCG': 'Ser', 'TCD': 'Ser', 'ATY': 'Ile', 'TCB': 'Ser', 'TCC': 'Ser', 'TCA': 'Ser', 'GCA': 'Ala', 'GCC': 'Ala', 'GCB': 'Ala', 'GCD': 'Ala', 'GCG': 'Ala', 'CGH': 'Arg', 'TRA': '***', 'GCH': 'Ala', 'GCK': 'Ala', 'YTR': 'Leu', 'CGK': 'Arg', 'CAY': 'His', 'GCN': 'Ala', 'GCS': 'Ala', 'GCR': 'Ala', 'GCT': 'Ala', 'GCW': 'Ala', 'GCV': 'Ala', 'GCY': 'Ala', 'YTG': 'Leu', 'YTA': 'Leu', 'MGA': 'Arg', 'MGG': 'Arg', 'CGN': 'Arg', 'MGR': 'Arg', 'ACA': 'Thr', 'CTT': 'Leu', 'ATG': 'Met', 'CTV': 'Leu', 'CTW': 'Leu', 'ACG': 'Thr', 'ATC': 'Ile', 'CTR': 'Leu', 'ATA': 'Ile', 'ACK': 'Thr', 'ACH': 'Thr', 'ACN': 'Thr', 'ATH': 'Ile', 'CTD': 'Leu', 'ACR': 'Thr', 'ATT': 'Ile', 'CTG': 'Leu', 'ACW': 'Thr', 'CTA': 'Leu', 'CTB': 'Leu', 'CTC': 'Leu', 'CTM': 'Leu', 'ACY': 'Thr', 'CTH': 'Leu', 'CTK': 'Leu', 'GGT': 'Gly', 'GGW': 'Gly', 'GGV': 'Gly', 'CGM': 'Arg', 'GGS': 'Gly', 'GGR': 'Gly', 'CGA': 'Arg', 'CGC': 'Arg', 'CGB': 'Arg', 'GGY': 'Gly', 'CGD': 'Arg', 'CGG': 'Arg', 'CGY': 'Arg', 'GGD': 'Gly', 'GGG': 'Gly', 'GGA': 'Gly', 'GGC': 'Gly', 'GGB': 'Gly', 'GGM': 'Gly', 'CGS': 'Arg', 'CGR': 'Arg', 'CGT': 'Arg', 'CGW': 'Arg', 'CGV': 'Arg', 'GTA': 'Val', 'GTB': 'Val', 'GTC': 'Val', 'GTD': 'Val', 'GTG': 'Val', 'GTH': 'Val', 'GTK': 'Val', 'GTM': 'Val', 'GTN': 'Val', 'GTR': 'Val', 'GTS': 'Val', 'GTT': 'Val', 'GTV': 'Val', 'GTW': 'Val', 'GTY': 'Val', 'GGN': 'Gly', 'GGH': 'Gly', 'GGK': 'Gly', 'AAG': 'Lys', 'AAA': 'Lys', 'AAC': 'Asn', 'CAR': 'Gln', 'CAT': 'His', '---': '---', 'AAT': 'Asn', 'AAR': 'Lys', 'CAC': 'His', 'CAA': 'Gln', 'AAY': 'Asn', 'TGT': 'Cys', 'CAG': 'Gln', 'TGY': 'Cys', 'GAR': 'Glu', 'TGC': 'Cys', 'TGA': '***', 'TGG': 'Trp', 'GAG': 'Glu', 'GAC': 'Asp', 'GAA': 'Glu', 'CTS': 'Leu', 'GAY': 'Asp', '~~~': '---', 'TTR': 'Leu'}
	
IUPAC = {'A':['A'], 'B':['C', 'G', 'T'], 'C':['C'], 'D':['A', 'G', 'T'], 
'G':['G'], 'H':['A', 'C', 'T'], 'K':['G', 'T'], 'M':['A', 'C'], 
'N':['G', 'A', 'T', 'C'], 'R':['A', 'G'], 'S':['C', 'G'], 'T':['T'], 
'V':['A', 'C', 'G'], 'W':['A', 'T'], 'Y':['C', 'T']}

IUPAC_rev = {('A',): 'A',
 ('A', 'C'): 'M',
 ('A', 'C', 'G'): 'V',
 ('A', 'C', 'T'): 'H',
 ('A', 'G'): 'R',
 ('A', 'G', 'T'): 'D',
 ('A', 'T'): 'W',
 ('C',): 'C',
 ('C', 'G'): 'S',
 ('C', 'G', 'T'): 'B',
 ('C', 'T'): 'Y',
 ('G',): 'G',
 ('G', 'A', 'T', 'C'): 'N',
 ('G', 'T'): 'K',
 ('T',): 'T'}
	
# Dictionaries for numerical encodong

nnDict = {'D':1, 'E':2, 'C':3, 'N':4, 'F':5, 'T':6, 'M':7, 'S':8, 'Y':9, 'Q':10, \
		  '.':11, '-':11, '~':11, 'W':12, 'I':13, 'V':14, 'L':15, 'A':16, 'G':17, 'P':18, \
           'H':19, 'K':20, 'R':21, '*':22}

nuclDict = {'A':1, 'C':2, 'G':3, 'T':4, '.':6, '-':6, '~':6}

nuclWithAmbig = {'A':1, 'C':2, 'G':3, 'T':4, 'M':5, '.':6, '-':6, '~':6, 'R':7, 'W':8, 'S':9, \
				  'Y':10, 'K':11, 'V':12, 'H':13, 'D':14, 'B':15, 'N':16}

#dictionary to define genome coverage (all gaps are 0, everything else is 1)
anuclCoverageS = {'A':1, 'C':1, 'G':1, 'T':1, 'M':1, '.':0, '-':0, '~':0, 'R':1, 'W':1, 'S':1, \
				  'Y':1, 'K':1, 'V':1, 'H':1, 'D':1, 'B':1, 'N':1}
				  
numDict = {'nucl': nuclDict, 'anucl': nuclWithAmbig, 'aa': nnDict, 'cvg': anuclCoverageS}

oneToThreeLetterAADict = {'*': '***', '-': '---', '.': '...', 'A': 'ALA', 'C': 'CYS', 'E': 'GLU', 'D': 'ASP', 'G': 'GLY', 'F': 'PHE', 'I': 'ILE', 'H': 'HIS', 'K': 'LYS', 'M': 'MET', 'L': 'LEU', 'N': 'ASN', 'Q': 'GLN', 'P': 'PRO', 'S': 'SER', 'R': 'ARG', 'T': 'THR', 'W': 'TRP', 'V': 'VAL', 'Y': 'TYR'}


#threeToOneLetterAADict = {'ILE': 'I', 'GLN': 'Q', '---': '-', 'GLY': 'G', 'GLU': 'E', 'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'LYS': 'K', 'PRO': 'P', 'ASN': 'N', '...': '.', 'VAL': 'V', 'THR': 'T', 'HIS': 'H', '***': '*', 'TRP': 'W', 'PHE': 'F', 'ALA': 'A', 'MET': 'M', 'LEU': 'L', 'ARG': 'R', 'TYR': 'Y'}

threeToOneLetterAADict = {'Val': 'V', '---': '-', 'Cys': 'C', 'Asp': 'D', 'Phe': 'F', 'Met': 'M', 'Leu': 'L', 'Asn': 'N', 'Tyr': 'Y', '...': '.', 'Ile': 'I', 'Gln': 'Q', 'Thr': 'T', 'Gly': 'G', 'His': 'H', '***': '*', 'Trp': 'W', 'Glu': 'E', 'Ser': 'S', 'Lys': 'K', 'Pro': 'P', 'Ala': 'A', 'Arg': 'R', 'Xaa': 'X', 'Xxx': 'X'}

def makeBackTransDict( translationDict ):
	"""create a dictionary keyed by aa that returns a tuple of codons"""
	
	dictOut = {}
	for codon in translationDict.keys():
		dictOut[ translationDict[codon] ] = (codon,) + dictOut.get( translationDict[codon] , () )
		
	return dictOut
	
backTransDictNoAmb = makeBackTransDict( translationWithoutAmbiguity )

complementDict = {'A': 'T', 'C': 'G', 'B': 'V', 'D': 'H', 'G': 'C', 'H': 'D', 'K': 'M', '-': '-', 'M': 'K', 'N': 'N', 'S': 'S', 'R': 'Y', 'U': 'A', 'T': 'A', 'W': 'W', 'V': 'B', 'Y': 'R','.':'.', '~':'~'}


# tools for constructing translation tables
#def formatDict(dictIn, width=6):
#	"""Returns a string that can be re-imported as the original
#	dictionary."""
#	
#	keys = dictIn.keys()
#	keys.sort()
#	
#	strout = ''
#	for i in range(len(keys)):
#		if i>0 and i%width == 0: strout += '\n'
#		strout += """%s:%s, """ % (`keys[i]`, `dictIn[keys[i]]`)
#		
#	return '{' + strout[:-2] + '}'
#	
#def makeAmbDict(ambDict=IUPAC):
#	"""Generate translation table with ambiguities."""
#	
#	chars = IUPAC.keys()
#	chars.sort()
#	
#	# make all combos of ambiguous codons
#	ambcodons = []	
#	for pos1 in chars:
#		for pos2 in chars:
#			for pos3 in chars:
#				ambcodons.append(pos1 + pos2 + pos3)
#	
#	
#	ambDict = {}
#	for codon in ambcodons:
#		# make all possible unambiguous codons
#		unamblist = []
#		aalist = []
#		print '************'
#		print codon #debug
#		for pos1 in IUPAC[codon[0]]:
#			for pos2 in IUPAC[codon[1]]:
#				for pos3 in IUPAC[codon[2]]:
#					thisCodon = pos1 + pos2 + pos3
#					unamblist.append(thisCodon) # debug
#					aalist.append(translationWithoutAmbiguity[thisCodon])
#		print unamblist # debug
#		print aalist
#		if max(aalist) == min(aalist):
#			ambDict[codon] = aalist[0]
#			print 'OK' # debug
#			
#	return ambDict
#
#
#def threeLetterTranslationTable():
#	threeLetterAAStr ="""
#Ala	A
#Arg	R
#Asn	N
#Asp	D
#Cys	C
#Gln	Q
#Glu	E
#Gly	G
#His	H
#Ile	I
#Leu	L
#Lys	K
#Met	M
#Phe	F
#Pro	P
#Ser	S
#*** *
#Thr	T
#Trp	W
#Tyr	Y
#Val	V
#--- -""".strip()
#	
#	threeLetterAADict = {}
#	for line in threeLetterAAStr.split('\n'):
#		threeLetter, oneLetter = line.split()
#		threeLetterAADict[oneLetter] = threeLetter
#		
#	translationWithoutAmbiguity3 = {}
#	for k in translationWithoutAmbiguity.keys():
#		translationWithoutAmbiguity3[k] = threeLetterAADict[translationWithoutAmbiguity[k]]
#
#	print 'translationWithoutAmbiguity3 =', translationWithoutAmbiguity3
#
#	translationWithAmbiguity3 = {}
#	for k in translationWithAmbiguity.keys():
#		translationWithAmbiguity3[k] = threeLetterAADict[translationWithAmbiguity[k]]
#
#	print 'translationWithAmbiguity3 =',translationWithAmbiguity3

	
