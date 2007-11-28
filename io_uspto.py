"""
I/O for USPTO sequence listing format sequences.
Public methods:
readSeqListing
"""

__version__ = "$Id: io_uspto.py 1487 2007-10-10 17:42:39Z n.hoffman $"

import re
from Seq import Seq
from sequtil import allButAlphaRexp, threeletter_to_oneletter_aa

class SeqListingFormatError(Exception):
	pass

taggedLineRexp = re.compile(r'(?P<tag><\d+>)?\s*(?P<data>.+)')

def _readSeqListingMetaData( instr ):
	
	dictOut = {}
	currentTag = '<0>' #catches everything before the first tag
	for line in instr.splitlines():
		if not line.strip(): continue
		tag, data = taggedLineRexp.findall(line)[0]
		
		if tag and tag != currentTag:
			currentTag = tag
		
		dictOut[currentTag] = (dictOut.get(currentTag, '') + 
		'\n' + data.strip()).strip()
				
	return dictOut

def _readSingleSeqListing( instr, seqTag ):
	"""Call this from readSeqListing. Return a dict keyed by numerical 
	field identifiers defined by USPTO containing RAW data."""
	
	dictOut = {}	
	lines = instr.splitlines()
	currentTag = '<0>'
	while 1:
		try:
			line = lines.pop(0)
		except IndexError:
			msg = 'A sequence entry is incomplete' 
			raise SeqListingFormatError, msg
		
		if not line.strip(): continue
		
		tag, data = taggedLineRexp.findall(line)[0]
		
		if tag and tag != currentTag:
			currentTag = tag
		
		dictOut[currentTag] = (dictOut.get(currentTag, '') + '\n' + data.strip()).strip()	
		
		if currentTag == seqTag: 
			# line with seqTag has been consumed; rest of lines should be sequence
			break
	
	dictOut[seqTag] = ' '.join(lines)
								
	return dictOut

isThreeLetterAARexp = re.compile('[A-Z][a-z][a-z]')

def _process_USPTO_dna_str( instr ):
	"""Removes protein translation by finding three-letter AA codes"""
	
	# find the three-letter AA translation
	instr = isThreeLetterAARexp.sub(' ', instr)
	
	return allButAlphaRexp.sub('', instr)

def readSeqListing( instr, matter='', client='' ):
	"""Converts USPTO-format sequence listing to a SEQ object.
	see http://www.uspto.gov/web/offices/com/sol/og/con/files/cons082.htm
	Some metadata from sequence listing header is transferred to each sequence
	object. Matter and client keys override data in instr. 
	Returns list of Seq objects."""
	
	###### define magic strings and numbers
	inventorTag = '<110>'
	titleTag = '<120>'
	seqDelimiter = '<210>'
	seqLenTag = '<211>'
	typeTag = '<212>'
	organismTag = '<213>'
	matterClientTag = '<130>'
	seqTag = '<400>'

	dnaTypePTO = 'DNA'
	protTypePTO = 'PRT'
	
	dnaTypeEMBL = 'dna'
	protTypeEMBL = 'prot'
	###### define magic strings and numbers
		
	# split into header material, list of sequences
	rawSeqList = instr.split(seqDelimiter)
	
	# process metadata
	metaData = _readSeqListingMetaData(rawSeqList.pop(0))
	
	# use matter and client provided in function args if supplied
	if matter != '' or client != '':
		pass
	else:	
		# get matter, client
		try:
			client, matter = metaData[matterClientTag].split('/')	
		except KeyError:
			raise SeqListingFormatError, 'line %s is missing from header data' \
			% matterClientTag
		except ValueError:
			raise SeqListingFormatError, 'client/matter not properly specified on line %s'\
			% matterClientTag
	
	matter = matter.zfill(6)
	client = client.zfill(6)
	
	# begin to assemble comment; this is optional data
	commentList = []
	
	# always starts with matter
	commentList.append('MA: ' + matter)
	
	if metaData.has_key(titleTag):
		commentList.append(titleTag + ' ' + ' '.join(metaData[titleTag].split()))
	
	if metaData.has_key(inventorTag):
		commentList.append(inventorTag + ' ' + 
		'; '.join(metaData[inventorTag].split('\n')))

	seqList = []
	for s in rawSeqList:
		
		rawData = _readSingleSeqListing(seqDelimiter + s, seqTag)
				
		# sequence name
		name = rawData[seqDelimiter]
		
		# process sequence data, define TY according to type
		try:
			ptotype = rawData[typeTag].upper()
		except KeyError:
			raise SeqListingFormatError, 'Missing line %s from sequence %s' \
			% (typeTag, name)
		
		# there may be a tag before seqDelimiter appended to end of this sequence
		# derived from the followign sequence. Remove it.
		rawSeqData = rawData[seqTag].split('<')[0]
		
		
		#if ptotype == dnaTypePTO:
		if ptotype.find(dnaTypePTO) > -1:
			type = dnaTypeEMBL
			seq = _process_USPTO_dna_str(rawSeqData)
			#seq = removeAllButAlpha(rawData[seqTag])
		#elif ptotype == protTypePTO:
		elif ptotype.find(protTypePTO) > -1:
			type = protTypeEMBL
			seq = threeletter_to_oneletter_aa(rawSeqData)
		else:
			raise SeqListingFormatError, 'Incorrect data on line %s in sequence %s' \
			% (typeTag, name)
		
		# sequence length sanity check
		try:
			# may be of form 'LENGTH: 2160'
			statedLength = int(rawData[seqLenTag].split(':')[-1])
		except (KeyError,ValueError):
			raise SeqListingFormatError, 'Missing/incorrect line %s in sequence %s' \
			% (seqLenTag, name)
		
		actualLength = len(seq)
		if statedLength != actualLength:
			msg = 'stated length (%s) of sequence %s not equal to actual length (%s)\n|%s|' \
			% (statedLength, name, actualLength, seq)
			raise SeqListingFormatError, msg			
		
		thisCommentList = commentList[:]
		if rawData.has_key(organismTag):
			thisCommentList.append( organismTag + ' ' + rawData[organismTag] )
		
		if thisCommentList: hea = ' '.join(thisCommentList)
		else: hea = ' '

		seqData = {}
		# these are EMBL format tags
		seqData['TY'] = type
		seqData['MA'] = matter
		seqData['CL'] = client
		
		seqList.append(Seq(name=name, seq=seq, hea=hea, data=seqData))
		
	return seqList
	
def test():
	"""Test routines in this module"""
	
	import glob	
	infiles = glob.glob('testfiles/*.uspto')
	
	seqlist = []
	for file in infiles:
		s = open(file).read()
		seqlist += readSeqListing(s, matter='999999', client='888888')
	
	for seq in seqlist:
		print `seq`
	
