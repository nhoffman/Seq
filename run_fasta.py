#!/usr/local/bin/python 

"""Utilities for running and parsing fasta software."""

import sys, os, re, logging, copy, random, tempfile, string, commands, logging, pprint, glob
from sequtil import cast
import Seq
from __init__ import ExecutionError

###### copy this code into each module to set up logging
log = logging
#######################################

TEMPDIR = tempfile.gettempdir()
ALIGN_SUFFIX = '.falign'

try:
    USER = os.environ['USER']
except KeyError:
    USER = os.environ['LOGNAME']

FASTAPATH = '/usr/local/bin'

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
    f.write(Seq.io_fasta.write(seq_or_list))
    f.close()
    
    return fname
    
def get_path_or_write_file(seq, tempdir=TEMPDIR):
    """If seq is a Seq instance or list of Seq
    instances, returns the absolute path of a temporary file 
    containing the fasta format sequence; if a readable
    file, returns the absolute path."""
    
    try:
        path = os.path.abspath(seq)
    except AttributeError:
        path = make_temp_fasta(seq, tempdir)
    
    return path
    

def run(query, target, e_val=10, outputfile=None, fastapath=None, format=10, cleanup=True):
    
    """Returns a dict keyed by (seqname1,seqname2) pairs containing
    alignment data"""
    
    # see http://helix.nih.gov/apps/bioinfo/fasta3x.txt
    # format = 10 for machine-readable alignments, 0 for traditional aligns
    
    query_file = get_path_or_write_file(query)
    target_file = get_path_or_write_file(target)
    
    if fastapath:
        fasta_prog = os.path.join(fastapath, 'fasta34')
    else:
        fasta_prog = os.path.join(FASTAPATH, 'fasta34')
    
    cwd = os.path.abspath(os.getcwd())

    if not outputfile:
        outputfile = os.path.join(TEMPDIR, randomname(12)+ALIGN_SUFFIX)
    else:
        outputfile = os.path.join(cwd, outputfile)

    # -A Force Smith-Waterman alignment
    # -H Omit Histogram
    # -q Quiet - does not prompt for any input.
    # -m format
    # -z 0 estimates the significance of the match from the mean and standard deviation of the library scores, without correcting for library sequence length.
    # -d number of sequences to display
    # -E maximum expect value to display

    fastacmd = ' '.join("""
    %(fasta_prog)s
    -A
    -H
    -q
    -z 0
    -m %(format)s
    -O %(outputfile)s
    %(query_file)s 
    %(target_file)s""".split())
    
    cmd = fastacmd % locals()
    log.info( cmd )

    cmd_output = commands.getoutput(cmd)
    log.debug(cmd_output)
    
    # check for successful execution
    if not os.access(outputfile,os.F_OK):
        log.critical('The following command failed:')
        log.critical(cmd)
        log.critical('...with output:')
        log.critical(cmd_output)
        raise ExecutionError, cmd_output
        
    # parse the data
    data = parseFasta(open(outputfile).read())
    
    if cleanup:
        tempfiles = set(glob.glob(os.path.join(TEMPDIR, '*.fasta')) + \
            glob.glob(os.path.join(TEMPDIR, '*' + ALIGN_SUFFIX)))
        for f in [query_file, target_file, outputfile]:
            if f in tempfiles:
                #log.debug('removing %s' % f)
                os.remove(f)
        query_file = target_file = outputfile = None

    for k in data.keys():   
        data[k]['file_q'] = query_file
        data[k]['file_t'] = target_file
        data[k]['file_out'] = outputfile    
    
#   pprint.pprint(data)
#   sys.exit()
    
    return data
    
def get_tup(s, prefix=None):
    
    key, val = s.strip().split(':')
    
    key = key.replace('-','_')
    
    
    if prefix:
        return '%s_%s' % (prefix, key), cast(val.strip())
    else:
        return key, cast(val.strip())


def parseFasta(instr):
    """Extracts various data from output of fasta34 with -m 10
    return a dict of dicts keyed by string seqid. Restrict parsed output to
    N=max_hits top matches."""
        
    # remove footer
    instr, _ = instr.split('>>><<<')
    
    # remove header
    try:
        _, instr = instr.split('>>>')
    except ValueError:
        raise FormatError, 'The input file contains no significant alignments:\n\n' + instr
            
    datablocks = instr.split('>>')

    # first block isn't useful
    datablocks.pop(0)
    
    outputData = {}
        
    for i, block in enumerate(datablocks):
        
        #log.debug('\n%(i)i ------>\n%(block)s\n<------- %(i)i' % locals())
        
        # consumes the first line
        firstline, block = block.split('\n',1)
        
        seqid = firstline.split()[0]
        
        header, query, target = block.split('>')
        
        # get the sequence names
        qlines = query.split(';')
        q_name = qlines.pop(0).split()[0]

        tlines = target.split(';')
        t_name = tlines.pop(0).split()[0]   

        this_key = tuple([q_name, t_name])
        # should restrict output to top hsp of each sequence pair
        if outputData.has_key(this_key):
            continue

        ## process the header info
        d = dict([get_tup(e) for e in header.split(';') if e.strip()])
        
        ## process the query            
        qlines[-1], q_al_str = qlines[-1].strip().split('\n',1)
        
        q_data = dict([get_tup(e, 'q') for e in qlines if e.strip()])
        
        d['q_al_str'] = q_al_str.replace('\n','')
        
        ## process the target           
        tlines[-1], fa_al_str = tlines[-1].strip().split('\n',1)
        d['fa_al_str'] = fa_al_str.replace('\n','')
        
        tlines[-2], t_al_str = tlines[-2].strip().split('\n',1)
        d['t_al_str'] = t_al_str.replace('\n','')
        
        t_data = dict([get_tup(e, 't') for e in tlines if e.strip()])
        
        ## add data
        d['q_name'] = q_name
        d.update(q_data)

        d['t_name'] = t_name
        d.update(t_data)    
        
        #add_calculated_values(d)
        assert not outputData.has_key(this_key)
        
        outputData[this_key] = d
            
#   log.debug('output data:')
#   log.debug(pprint.pformat(outputData))
    
    return outputData



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

def show_alignment(row, width=60, align=True):
    
    print """%(q_name)s x %(t_name)s    sw_ident = %(sw_ident)s 
    files: %(file_q)s %(file_t)s %(file_out)s
    """.strip() % row
        
    if align:
        keys = 'q_al_str fa_al_str t_al_str'.split()
        for q,a,t in zip(*[Seq.sequtil.wrap(row[k],width,'list') for k in keys]):
            print q
            print a
            print t
            print ''
    

def main():
    
    
    test_input = os.path.abspath('../testfiles/10patients.fasta')
    print 'reading fasta format file %s' % test_input
    seqlist = Seq.io_fasta.readFasta(open(test_input).read())
    
    query, target = seqlist[0], seqlist[1:] 
    
    pairs = runfasta(query, target, cleanup=False)
    print 'master dict keyed by: %s ...' % `pairs.keys()[:10]`
    print 'each dict keyed by: ' + `pairs.values()[0].keys()`

    
    for k,v in sorted(pairs.items()):
        #pprint.pprint(v)
        
        print k, v['q_sq_len'], v['t_sq_len'],
        
        try:
            print v['bs_overlap'], v['bs_ident'] 
        except KeyError:
            print v['sw_overlap'], v['sw_ident']
        
        show_alignment(v)
        
    
    
    sys.exit()
        
    print 'trimming sequences'
    trimmed_seqlist = trim_align(seqlist, fasta_output_data)
    
    print 'query sequence:'
    print Seq.io_fasta.readFasta(open(query_file).read())[0]

    print 'first target sequence - trimmed'
    print trimmed_seqlist[0]
    
    print 'first target sequence - untrimmed'
    print seqlist[0]


    
if __name__ == '__main__':
    main()
