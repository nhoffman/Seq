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

def get_path_or_write_file(seq, outdir):
    """If seq is a Seq instance or list of Seq
    instances, returns the absolute path of a temporary file
    containing the fasta format sequence; if a readable
    file, returns the absolute path."""

    try:
        path = os.path.abspath(seq)
    except AttributeError:
        path = make_temp_fasta(seq, outdir)
        is_existing_file = False
    else:
        is_existing_file = True

    return path, is_existing_file


def run(query, target, e_val=10, outfile=None,
    fastapath=None, format=10, cleanup=True):

    """Returns a dict keyed by (seqname1,seqname2) pairs containing
    alignment data.

    * query - Seq object or filename of fasta format sequences
    * target - list of Seq objects or filename of fasta format sequences
    * e_val - (see FASTA3* documentation)
    * outfile - name of output file
    * outdir - directory to write fasta output
    * fastapath - name of directory containing fasta3* executable
    * format - (see FASTA3* documentation)
    * cleanup - if True, delete fasta output file
    """

    # see http://helix.nih.gov/apps/bioinfo/fasta3x.txt
    # format = 10 for machine-readable alignments, 0 for traditional aligns

    if outfile:
        outdir = os.path.abspath(os.path.split(outfile)[0])
    else:
        outdir = TEMPDIR
        outfile = os.path.join(outdir, randomname(12)+ALIGN_SUFFIX)

    query_file, query_is_file = get_path_or_write_file(query, outdir)
    target_file, target_is_file = get_path_or_write_file(target, outdir)

    fasta_prog = Seq.find_exec('fasta35', fastapath)
    if fasta_prog is None:
        raise OSError('fasta35 could not be found')

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
    -O %(outfile)s
    %(query_file)s
    %(target_file)s""".split())

    cmd = fastacmd % locals()
    log.info( cmd )

    cmd_output = commands.getoutput(cmd)
    log.debug(cmd_output)

    # check for successful execution
    if not os.access(outfile,os.F_OK):
        log.critical('The following command failed:')
        log.critical(cmd)
        log.critical('...with output:')
        log.critical(cmd_output)
        raise ExecutionError, cmd_output

    # parse the data
    data = parseFasta(open(outfile).read())

    if cleanup:
        if not query_is_file:
            os.remove(query_file)
        if not target_is_file:
            os.remove(target_file)
        os.remove(outfile)
        query_file = target_file = outfile = None

    for k in data.keys():
        data[k]['file_q'] = query_file
        data[k]['file_t'] = target_file
        data[k]['file_out'] = outfile

    return data

def get_tup(s, prefix=None):

    key, val = s.strip().split(':')

    key = key.replace('-','_')


    if prefix:
        return '%s_%s' % (prefix, key), cast(val.strip())
    else:
        return key, cast(val.strip())


def parseFasta(instr):
    """Extracts various data from output of fasta34/fasta35 with -m 10
    return a dict of dicts keyed by string seqid. Restrict parsed output to
    N=max_hits top matches."""

    # remove footer
    instr, _ = instr.split('>>><<<')

    # remove header
    try:
        _, _, instr = instr.split('>>>')
    except ValueError:
        raise FormatError, 'The input file contains no significant alignments:\n\n' + instr[:500]

    datablocks = instr.split('>>')

    # first block isn't useful
    datablocks.pop(0)

    outputData = {}

    for i, block in enumerate(datablocks):

        log.debug('\n%(i)i ------>\n%(block)s\n<------- %(i)i' % locals())

        # consumes the first line
        firstline, block = block.split('\n',1)

        seqid = firstline.split()[0]

        header, query, target = block.split('>')

        # process the header info
        log.debug('header:\n %s', header)
        d = dict([get_tup(e) for e in header.split(';') if e.strip()])
        log.debug('dict of header info:\n%s',pprint.pformat(d))
        
        # get the sequence names
        qlines = [e.strip() for e in query.split(';')]
        q_name = qlines.pop(0).split()[0]

        tlines = [e.strip() for e in target.split(';')]
        t_name = tlines.pop(0).split()[0]

        this_key = tuple([q_name, t_name])

        # restrict output to top hsp of each sequence pair
        if this_key in outputData:
            continue

        # process the query
        log.debug('query:\n %s', query)
        q_data = {}
        for line in qlines:
            if line.startswith('al_display_start'):
                line, q_al_str = line.split('\n',1)
                q_data['q_al_str'] = q_al_str.replace('\n','') 

            k, v = get_tup(line, 't')
            q_data[k] = v

        log.debug('dict of query info:\n%s',pprint.pformat(q_data))
        
        ## process the target
        log.debug('target:\n %s', target)

        t_data = {}
        for line in tlines:
            if line.startswith('al_cons'):
                continue
            elif line.startswith('al_display_start'):
                line, t_al_str = line.split('\n',1)
                t_data['t_al_str'] = t_al_str.replace('\n','')

            k, v = get_tup(line, 't')
            t_data[k] = v

        log.debug('dict of target info:\n%s',pprint.pformat(t_data))
            
        ## add data
        d['q_name'] = q_name
        d.update(q_data)

        d['t_name'] = t_name
        d.update(t_data)
        
        #add_calculated_values(d)
        assert not outputData.has_key(this_key)

        log.debug('Data from this aligned pair: %s\n' % pprint.pformat(d))
        
        outputData[this_key] = d

#   log.debug('output data:')
#   log.debug(pprint.pformat(outputData))

    log.info('%s alignments processed: \n%s' % (len(outputData), pprint.pformat(outputData.keys())))
        
    return outputData

# def tabulate_results(fasta_results, headers=None):
#     """
#     Create a taular representation of results of fasta3*
#     
#     * fasta_results - output of parseFasta (a dict of dicts keyed by ('qname','tname'))
#     
#     Returns a tab-delimited string.
#     """
#     
#     # TODO: implement me
#     
#     pass
    
    
    
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

