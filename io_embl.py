"""
I/O for EMBL format sequences.
Public methods are:
read
write
readEMBLStr (deprecated)
writeEMBLStr (deprecated)
"""

__version__ = "$Id$"

import re, os, sys
import logging
import Seq
from sequtil import wrap, removeAllButAlpha

log = logging

class EMBLFormatError(TypeError):
	pass

def _writeEMBLLine(key, val, linelength ):
	
	lmar = 5
	fstr = '%-' + `lmar` + 's%s'
	
	strList = []
	strLen =  linelength-lmar
	if not val.strip(): 
		strList.append( fstr %(key, ' ') )
	else:
		# word wrap val
		valLines = wrap(val, strLen, output='list') 
		for line in valLines:
			strList.append( fstr %(key, line) )
			
	return os.linesep.join(strList)


def write( seqList, linelength=60, insert_blanklines=0 ):
	
	if type(seqList) != type([]):
		raise ValueError, 'input should be a list of Seq objects'
	
	l = linelength
	i = insert_blanklines
	return os.linesep.join([_writeSingleEMBLStr(s,l,i).strip() for s in seqList]) + os.linesep

def _writeEMBLSeq(seqStr, linelength):
	
	lmar = 5
	seqDelimiter = '//'
	linesep = os.linesep
	
	seqStr = removeAllButAlpha(seqStr)
	
	strList = []
	strList.append('SQ   sequence length %s;' % len(seqStr))
	strLen =  linelength-lmar
	for i in range( 0, len(seqStr), strLen): 
		strList.append( ' '*lmar + seqStr[i:i+strLen] )
			
	return linesep.join(strList) + linesep + seqDelimiter


def _writeSingleEMBLStr( seqObj, linelength, insert_blanklines ):
	"""Returns a string with mappings of Seq object characteristics as defined
	in _readSingleEMBLStr. Call this function from writeEMBLStr.
	"""

	nameKey = 'ID'
	accKey = 'AC'
	heaKey = 'DE'
	seqKey = 'SQ'
	commentKey = 'XX'
	seqDelimiter = '//'
	
	strList = []
	# name is required
	strList.append( _writeEMBLLine(nameKey, seqObj.name, linelength ))
	
	# accession and description are optional
	if hasattr(seqObj, 'acc'):
		strList.append( _writeEMBLLine(accKey, seqObj.acc, linelength ))
	if hasattr(seqObj, 'hea'):
		strList.append( _writeEMBLLine(heaKey, seqObj.hea, linelength ))
	
	# iterate over other keys in data
	for k in seqObj.keys:
		if k in ['acc','hea']:
			continue
		strList.append( _writeEMBLLine(k[:2].upper(), getattr(seqObj,k), linelength ))
	
	# sequence is required
	strList.append( _writeEMBLSeq( seqObj.seq, linelength ) )
	
	if insert_blanklines:
		entrysep = os.linesep + commentKey + os.linesep
	else:
		entrysep = os.linesep
	
	return entrysep.join(strList)
		
def read( strin ):
	"""Reads data corresponding to one or more sequences in EMBL format.
	Return a list of Seq objects"""
	
	seqDelimiter = '//'
	strList = strin.split(seqDelimiter)
	
	seqList = []
	for s in strList:
		if not s.strip(): continue
		s = s.strip() + os.linesep + seqDelimiter		
		seqList.append( _readSingleEMBLStr(s) )
	
	return seqList

def _readEMBLLine( line ):
	"""Returns key, val where key is always an uppercase, two-letter key
	(len(key)!=2 results in EMBLFormatError). key is the first word on the line;
	val may be an empty string."""
	
	splitline = line.split(None,1)
	
	try:
		key, val = splitline
	except ValueError:
		key = splitline[0]
		val = ''
	
	if len(key) != 2:
		raise EMBLFormatError, 'the key %s is not 2 characters'%key
	return key.upper(),val	

# define these rexp externally to avoid multiple re calls
wsAndDigitsRexp = re.compile(r'[\d\s]+')
	
def _readSingleEMBLStr( strin ):
	"""input is a single sequence in EMBL format (expects terminal //); 
	returns a single Seq object. Mappings from EMBL two-letter line identifiers to Seq
	fields are as follows:
	ID   name (sequence name as one word)
	AC   acc (an arbitrary accession number)
	DE   hea (an arbitrary header string)
	SQ   seq (DNA or AA sequence string)
	all other lines identified by two-letter keys will be parsed and 
	placed in the Seq.__data dict
	
	Parsing does not strictly adhere to the 5-space gutter on the left;
	for example, the following lines result in the same output:
	
	cl a client
	CL   a client
	"""
	
	nameKey = 'ID'
	accKey = 'AC'
	heaKey = 'DE'
	seqKey = 'SQ'
	commentKey = 'XX'
	seqDelimiter = '//'
	namedKeys = [nameKey, accKey, heaKey, seqKey]
	requiredKeys = [nameKey, seqKey, seqDelimiter]
	
	# look for some key features defining EMBL format
	k = ''
	try:
		for k in requiredKeys:
			strin.index(k)
	except ValueError:
		raise EMBLFormatError, 'Formatted sequence is missing the "%s" key' % k
	
	lines = strin.strip().splitlines()
	lines.pop(-1) # consume final //
		
	currentKey = ''
	IDcount = 0
	allData = {}
	while 1:
		line = lines.pop(0)
		if not line.strip: continue 
		key, val = _readEMBLLine(line)

		if key == commentKey: continue
		if key == nameKey: IDcount += 1
		
		if key and key != currentKey: 
			currentKey = key
		
		allData[currentKey] = allData.get(currentKey,'') + ' ' + val
		if currentKey == seqKey: break
	
	if IDcount > 1:
		raise EMBLFormatError, 'More than one line begins with %s ' % nameKey
	
	# remaining lines represent sequence info
	seqStr = wsAndDigitsRexp.sub('', ''.join(lines) )
	if seqStr == '':
		raise EMBLFormatError, 'No sequence string found in this record'
	
	# initialize Seq object
	try:
		name = allData[nameKey].split()[0]
	except (IndexError, KeyError):
		raise EMBLFormatError, 'No ID key (name not specified)'
		
	acc = allData.get(accKey,'').strip()
	hea = allData.get(heaKey,'').strip()
	
	for key in namedKeys:
		try: del allData[key]
		except KeyError: pass
	
	data = {}
	for key, val in allData.items():
		data[key] = val.strip()
		
	# def __init__( self, name, seq, type='', acc='',hea='' ):
	return Seq.Seq(name, seqStr, type='', acc=acc, hea=hea, data=data)

# for backward compatibility
def readEMBLStr(instr):
    log.info('io_embl.readEMBLStr is deprecated: use io_embl.read instead')
    return read(instr)

def writeEMBLStr(seqs):
    log.info('io_embl.writeEMBLStr is deprecated: use io_embl.write instead')
    return write(seqs)
	