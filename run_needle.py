#!/usr/local/bin/python 

"""Utilities for running and parsing output from EMBOSS needle."""

import sys, os, re, logging, time, copy, random, tempfile, string, commands, logging, pprint, glob

import sequtil
from sequtil import wrap, cast, decode_aln, pid_m1, pid_m2, pid_m3
import io_fasta

###### copy this code into each module to set up logging
log = logging
#######################################

TEMPDIR = tempfile.gettempdir()
ALIGN_SUFFIX = '.needle'

EDNAFULL = os.path.join(os.path.abspath(os.path.split(__file__)[0]),'data','EDNAFULL')
#EDNAFULL = os.path.join(sys.prefix, 'lib', 'python'+sys.version[:3],'site-packages','Seq','data','EDNAFULL')

try:
	USER = os.environ['USER']
except KeyError:
	USER = os.environ['LOGNAME']

EXEC_PATH = '/usr/local/bin'

class FormatError(Exception):
	pass

def randomname(length=12):
	
	letters = string.letters
	chars = string.letters + string.digits
	
	return ''.join([random.choice(letters)]+[random.choice(chars) for i in range(length-1)])
	
def make_temp_fasta(seq_or_list, tempdir):
	"""Writes a sequence object or list of objects to a temporary 
	file with random name and returns the absolute path to the file."""
	
	fname = os.path.join(tempdir, randomname(12) + '.fasta')
	f = open(fname, 'w')
	f.write(io_fasta.write(seq_or_list))
	f.close()
	
	return fname
	
def get_path_or_write_file(seq, tempdir=TEMPDIR):
	"""If seq is a Seq instance or list of Seq
	instances, , returns the absolute path of a temporary file 
	containing the fasta format sequence; if a readable
	file, returns the absolute path."""
		
	try:
		assert os.access(seq, os.F_OK)
	except AssertionError:
		raise IOError, 'The file %s cannot be read' % seq
	except TypeError:
		return make_temp_fasta(seq, tempdir)
	else:
		return os.path.abspath(seq)

def needle(query, target, outputfile=None, exec_path=None, submat=None, cleanup=True):
	
	"""Returns a dict keyed by (seqname1,seqname2) pairs containing
	alignment data
	query, target - either a list of Seq objects or the path to a fasta file
	outputfile - optional filename for output of needle
	exec_path - optional directory containing needle program; default is /usr/local/bin
	submat - optional path to a substitution matrix
	cleanup - if True, delete needle output after it is parsed
	"""
	
	# see http://bioweb.pasteur.fr/docs/EMBOSS/needle.html
	
	query_file = get_path_or_write_file(query)
	target_file = get_path_or_write_file(target)
	
	if exec_path:
		needle_prog = os.path.join(exec_path, 'needle')
	else:
	    # use default location for installed apps
		needle_prog = os.path.join(EXEC_PATH, 'needle')
	
	cwd = os.path.abspath(os.getcwd())

	if not outputfile:
		outputfile = os.path.join(TEMPDIR, randomname(12)+ALIGN_SUFFIX)
	else:
		outputfile = os.path.join(cwd, outputfile)
	
	if submat:
		use_submat = '-datafile "%s"' % os.path.abspath(submat)
	else:
		use_submat = ''
	
	cmd = """
	%(needle_prog)s 
	%(use_submat)s
	-asequence %(query_file)s
	-bsequence %(target_file)s
	-outfile %(outputfile)s
	-aglobal3 
	-gapopen 10 
	-gapextend 0.5 
	-nobrief 
	-aformat3 markx10"""
	
	cmd = ' '.join(cmd.split()) % locals()
	log.debug( cmd )

 	cmd_output = commands.getoutput(cmd)
	log.debug(cmd_output)
		
	if not os.access(outputfile, os.F_OK):
		raise IOError, cmd_output
	
	# parse the data
	data = parseNeedle(open(outputfile).read())
		
	if cleanup:
		tempfiles = set(glob.glob(os.path.join(TEMPDIR, '*.fasta')) + \
			glob.glob(os.path.join(TEMPDIR, '*' + ALIGN_SUFFIX)))
		for f in [query_file, target_file, outputfile]:
			if f in tempfiles:
				#log.debug('removing %s' % f)
				os.remove(f)
		query_file = target_file = outputfile = None
	else:	
		for k in data.keys():	
			data[k]['file_q'] = query_file
			data[k]['file_t'] = target_file
			data[k]['file_out'] = outputfile	
	
# 	pprint.pprint(data)
# 	sys.exit()
	
	return data
	
def get_tup(s, prefix=None):
	
	key, val = s.strip().split(':')
	
	key = key.replace('-','_')
	
	if prefix:
		return '%s_%s' % (prefix, key), val.strip()
	else:
		return key, val.strip()


def parseNeedle(instr):
	"""Extracts various data from output of needle with
	-aformat3 markx10
	return a dict of dicts keyed by string seqid.
	
	adds keys q_al_enc, t_al_enc to each dict D 
	such that the following is true:
	
	aligned = D['q_al_str']
	degapped = aligned.replace('-','')
	aligned == sequtil.decode_aln(degapped, eval(D['q_al_enc']))
	"""
	
	# do we have the correct format?
	assert instr.find('Align_format: markx10') != -1
	
	# remove footer
	instr, _, _ = instr.rsplit('#',2)
		
	# remove header
	datablocks = instr.split('>>>')
	datablocks.pop(0)
	
	outputData = {}
	for i, block in enumerate(datablocks):
		
		# lop off the commented data and run parameters
		block = block.split('#=====')[0]
		block = block.split('>>#')[1]
		
# 		log.debug('\n%(i)i ------>\n%(block)s\n<------- %(i)i' % locals())
		
		# consumes the first line
		align_no, block = block.split('\n',1)
		
		assert int(align_no) == i+1
		
		header, query, target = block.split('>')
		
		# get the sequence names
		q_name, query = query.split('..',1)
		t_name, target = target.split('..',1)
	
		this_key = tuple(sorted([q_name.strip(), t_name.strip()]))

		## process the header info
		d = dict([get_tup(e) for e in header.split(';') if e.strip()])
		
		## process the query and target			
		q_data = dict([get_tup(e, 'q') for e in query.split(';') if e.strip()])
		t_data = dict([get_tup(e, 't') for e in target.split(';') if e.strip()])

		## add data
		d['q_name'] = q_name
		d.update(q_data)

		d['t_name'] = t_name
		d.update(t_data)
				
		d['q_al_display_start'], q_al_str = d['q_al_display_start'].split('\n',1)
		d['t_al_display_start'], t_al_str = d['t_al_display_start'].split('\n',1)
		
		d['q_al_str'] = q_al_str.replace('\n','').upper()
		d['t_al_str'] = t_al_str.replace('\n','').upper()
		
		d['q_al_enc'] = `sequtil.encode_aln(d['q_al_str'], gapchar='-', self_check=True)`
		d['t_al_enc'] = `sequtil.encode_aln(d['t_al_str'], gapchar='-', self_check=True)`
		
		assert not outputData.has_key(this_key)
		
		d = dict((k,cast(v)) for k,v in d.items())
		add_calculated_values(d)
		
		outputData[this_key] = d
			
# 	log.debug('output data:')
# 	log.debug(pprint.pformat(outputData))
		
	return outputData

def add_calculated_values(d):
	
	starting_keys = set(d.keys())
	
	q_al_str, t_al_str = d['q_al_str'], d['t_al_str']
	start, stop = find_end_gaps(q_al_str, t_al_str)
	
	q_list, t_list = list(q_al_str)[start:stop], list(t_al_str)[start:stop]

	d['trim_start'] = start
	d['trim_stop'] = stop		
	d['pid_m1'] = pid_m1(q_list, t_list)
	d['pid_m2'] = pid_m2(q_list, t_list)
	d['pid_m3'] = pid_m3(q_list, t_list)
		
	ending_keys = set(d.keys())
	
	#print 'added the following keys: '+`ending_keys-starting_keys`
	
	
trim_rexp = re.compile(r'(?P<leading>^-+)?.+?(?P<trailing>-+)?$')
def find_end_gaps(q_al_str, t_al_str):
	"""
	trim end gaps from align strings:
	
	-----XXXXXXXXXXXXXXXXXXXXXXX
	YYYYYYYYYYYYYYYYYYYY--------
	
	becomes 

	XXXXXXXXXXXXXXX
	YYYYYYYYYYYYYYY
	
	return q_al_str, t_al_str
	note that the trimmed string is obtained with, eg
	q_al_str[startpos:endpos]
	"""
	
	assert len(q_al_str) == len(t_al_str)
	
	q_groups = trim_rexp.match(q_al_str).groups()
	t_groups = trim_rexp.match(t_al_str).groups()
		
	# determine leading coords
	try:
		startpos = len(max([q_groups[0], t_groups[0]]))
	except TypeError:
		startpos = 0
	
	try:
		endpos = len(q_al_str) - len(max([q_groups[1], t_groups[1]]))
	except TypeError:
		endpos = len(q_al_str)
	
	return startpos, endpos
	
def trim_align(seqlist, align_data):
	"""Assumes align_data is keyed by seq.getName(). Returns
	a new list of Seq objects, trimmed according to al_start
	and al_stop. Reverse-complements the sequence if necessary
	according to the orientation in the input alignment.
	"""
	
	trimmed_seqs = []
 	for seq in seqlist:
 		name = seq.getName()
		
		if not align_data.has_key(name):
			log.info('the sequence %(name)s was not found in the alignment data' % locals())
			continue
			
		these_results = align_data[name]

		start = these_results['al_start']
		stop = these_results['al_stop']
		
		substr = seq[start - 1:stop]
		
		log.debug('name: %(name)s start: %(start)s stop: %(stop)s' % locals())
		
		if these_results['fa_frame'] == 'r':
			substr = Seq.reverse_complement(substr)
			log.debug('seq %s frame=%s, reverse complementing seq:\n%s' % (name, these_results['fa_frame'], substr))
			
		newseq = copy.deepcopy(seq)
		newseq.setSeq(substr)
		trimmed_seqs.append(newseq)
		
	return trimmed_seqs


def print_align(q_al_str, t_al_str, width):
	
	for q,t in zip(wrap(q_al_str,width,'list'), wrap(t_al_str,width,'list')):
		print q
		print t
		print ''

def show_record(row, width=60, align=True):
	
	for c in sorted(row.keys()):
		if c.endswith('_al_str'):
			continue 
		print '%s : %s'%(c,row[c])
	
	if align:
		start, stop = row['trim_start'], row['trim_stop']
		q_al_str, t_al_str = row['q_al_str'], row['t_al_str']
		
		print 'aligned strings'
		print_align(q_al_str, t_al_str, width)
		print 'q_aln_str[%(start)s:%(stop)s], t_aln_str[%(start)s:%(stop)s]' % locals()
		print_align(q_al_str[start:stop], t_al_str[start:stop], width)

def main():
		
	logging.basicConfig(level=logging.DEBUG, format='%(lineno)s %(levelname)s %(message)s', stream=sys.stdout)
	
	test_input = os.path.abspath('testfiles/10patients.fasta')
	print 'reading fasta format file %s' % test_input
	seqlist = io_fasta.read(open(test_input).read())
	
	query, target = seqlist[0], seqlist[1:] 
	
 	pairs = needle(query, target, cleanup=True, submat='data/EDNAFULL')
 	print 'master dict keyed by: %s ...' % `pairs.keys()[:10]`
 	print 'each dict keyed by: ' + `pairs.values()[0].keys()`
	
	for k,v in sorted(pairs.items()):
		show_record(v, align=True)
		print '*'*30
		
if __name__ == '__main__':
	main()
