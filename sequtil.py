import re
import copy
import random
import string
import Seq
import os
import logging

log = logging

from Dictionaries import translationWithoutAmbiguity, translationWithAmbiguity, translationWithoutAmbiguity3, translationWithAmbiguity3, complementDict, threeToOneLetterAADict, IUPAC_rev

__version__ = '$Id$'

#to find all single gaps
singleGapsReo = re.compile( r'[-.~]', re.I)

#fasta recognizing pattern
fastaPattern = r'>(?P<name>[ \t]*\S+)[ \t]*(?P<hea>.*)\n(?P<seq>[-*a-z~.\s?]+)\n'
fastaPatternReo = re.compile( fastaPattern, re.I )

#selexPattern = r"^[ \t]*(?P<name>\S+)[ \t]+(?P<seq>[-_*a-z~. ]+)\n"
selexPattern = r"^\s*(?P<name>\S+)\s+(?P<seq>[-_*a-z~. \t]+)\n"
selexPatternReo = re.compile( selexPattern, re.I | re.M )

# recognizes whitespace, digits, and non-alphanumeric characters
allButAlphaRexp = re.compile(r'[^a-zA-Z]')

def randomname(length=10):
    choice = random.choice
    letters = string.letters
    return ''.join(choice(letters) for i in xrange(length))

def cast(instr):
    """Tries to cast instr as an int or float; returns instr
    if both fail."""

    if not isinstance(instr, str):
        return instr

    try:
        return int(instr)
    except ValueError:
        try:
            return float(instr)
        except ValueError:
            return instr.strip()

def translate( seq, table = 'ambi'):
    """seq      sequence object or a string; return type
                is determined by type passed
       table    {'ambi'|'unambi'}
                these are standard eukaryotic translation tables
                with or without ambiguity"""

    #retrieve translation table
    translationTableDict = \
    {'ambi':translationWithAmbiguity,
    'unambi':translationWithoutAmbiguity,
    'ambi3':translationWithAmbiguity3,
    'unambi3':translationWithoutAmbiguity3}

    table = translationTableDict.get(table, translationWithAmbiguity)

    # unknown character is X*1 or X*3
    unk = 'X'*len(table.values()[0])

    s = seq[:].upper() # now s is a string regardless of input type

    #convert all gap characters to dashes
    s = s.replace('.','-').replace('~','-')

    codons = [s[i:i+3] for i in range(0,len(s),3)]
    peplist = [table.get(c, unk) for c in codons]

    peptide = ''.join(peplist)

    if type( seq ) == type(''):
        return peptide
    else:
        #make sequence object
        newhea = '%s (translation)' % seq.hea
        seqObj = Seq.Seq( name=seq.name, seq=peptide, hea=newhea )
        return seqObj

def reverse(instr):
    """Reverse the order of characters in a string"""
    l = list(instr)
    l.reverse()
    return ''.join(l)

def complement(instr, revdict=complementDict):

    instr = instr.upper()
    return ''.join([complementDict.get(char,'X') for char in list(instr)])

def reverse_complement(instr, revdict=complementDict):

    l = list(instr.upper())
    l.reverse()
    return ''.join([complementDict.get(char,'X') for char in l])

def pid_m1(q_clist, t_clist):
    """
    Calculate fractional identity (ie, 0 <= fid <= 1) given two lists of
    characters representing an alignment of two sequences. Assumes
    end gaps have been removed.

    fid = identical characters/length of sequence

    Note that this method is likely to under-estimate similarity, since
    gaps are counted as a mismatch
    """

    assert len(q_clist) == len(t_clist)
    return len([1 for a,b in zip(q_clist,t_clist) if a==b])*1.0/len(q_clist)

def pid_m2(q_clist, t_clist):
    """
    Calculate fractional identity (ie, 0 <= fid <= 1) given two lists of
    characters representing an alignment of two sequences. Assumes
    end gaps have been removed.

    fid = identical non-gap chars/total non-gap chars

    Note that this method is likely to over-estimate similarity as gapped
    positions are ignored
    """

    assert len(q_clist) == len(t_clist)
    d = {True:1, False:0}
    matches = [d[a==b] for a,b in zip(q_clist,t_clist) if a!='-' and b!='-']
    return sum(matches)*1.0/len(matches)

def pid_m3(q_clist, t_clist):
    """
    Calculate fractional identity (ie, 0 <= fid <= 1) given two lists of
    characters representing an alignment of two sequences. Assumes
    end gaps have been removed.

    fid = identical non-gap chars/(total non-gap chars + number of gaps)

    Thus continuous run of gaps, regardless of length, results in a
    penalty of one mismatch.
    """

    assert len(q_clist) == len(t_clist)

    d = {True:1, False:0}
    matches = []
    in_gap = False
    for a,b in zip(q_clist,t_clist):
        this_match = None
        if a=='-' or b=='-':
            if not in_gap: # only first gap character is appended
                this_match = d[a==b]
            in_gap = True
        else:
            in_gap = False
            this_match = d[a==b]

        if this_match is not None:
            matches.append(this_match)

    return sum(matches)*1.0/len(matches)

def threeletter_to_oneletter_aa(instr):
    """Converts three-letter aa code to one-letter aa code.
    Ignores digits and whitespace. Three-letter aa abbreviations
    are expected to be whitespace-deleimited. This is kind of a hack."""

    #wordList = instr.upper().split()
    wordList = instr.split()

    d = threeToOneLetterAADict

    return ''.join([d[w] for w in wordList if d.has_key(w)])

def wrap(text, width=60, output='string'):
    """Wraps input string [text] to [width] characters.
    Set output=string for a newline-delimited string, output=list
    for a list of substrings."""

    r1 = range(0, len(text)+1, width)
    r2 = range(width, len(text) + width +1, width)

    lines = [text[f:t] for f,t in zip(r1,r2) if text[f:t].strip()]
    if output == 'string':
        return '\n'.join(lines) + '\n'
    else:
        return lines

def breakLines( s, n ):
    """introduce linebreaks every |n| characters
    in the string |s| and returns it"""

    output = []
    for i in range(0, len(s), n):
        output.append( s[i:i+n] )

    return '\n'.join(output)

def removeWhitespace( s ):
    """
    s:    string
    [v]   verbosity
    returns the string |s| with all whitespace characters
    removed"""

    removed = ''.join( s.split() )
    return removed

removeTrailingCommaRexp = re.compile(r',+$')
def removeTrailingComma(s):
    return removeTrailingCommaRexp.sub('', s)

def removeAllButAlpha(instr):
    return allButAlphaRexp.sub('', instr)

def gapstrip( seq, gapchars = singleGapsReo):
    """
    seq:         string or sequence object

    [gapchars]:  [singleGapsReo] or any compiled regular
                 expression; singleGapsReo matches r'[-.~]'
    [v]          verbosity

    Removes characters in |gapchar| expression from |s| and
    returns a new degapped sequence object or string (depending on object passed)."""

    #make a slice copy of s to allow handling of strings and sequence
    #objects
    s = seq[:]
    #replace all occurances of the object in the string s
    s = gapchars.sub( "", s )

    if type(seq) == types.StringType:
        return s
    else:
        #make sequence object
        seqObj = Seq.Seq( name=seq.getName(), seq=s, hea=seq.getHea() )
        return seqObj

def block(str, blocksize, output='string', rexp=r'\S'):
    """Returns a string containing space-delimited substrings
    (or list) of str of length blocksize. Output can be 'string' or 'list'."""
    if blocksize < 1:
        sys.exit('block(): blocksize must be >= 1')
    elif blocksize > len(str):
        return str

    expStr = rexp * blocksize #all nonwhitespace chars
    exp = re.compile(expStr)

    lis = exp.findall(str)

    if len(str) <= blocksize:
        remainder = (blocksize - len(str))*-1
    else:
        remainder = len(str)%blocksize*-1

    if remainder == 0:
        end = []
    else:
        end = [str[remainder:]]

    if output == 'string':
        return string.join(lis + end, ' ')
    elif output == 'list':
        return lis + end

def tabulate( seqList ):
    """calculate the abundance of each character in the columns of
    aligned sequences; tallies are returned as a list of dictionaries
    indexed by position (position 1 = index 0). Keys of dictionaries are
    characters appearing in each position (so dictionaries are
    of variable length).

    seqList:            a list of sequence objects

    returns a list of dictionaries corresponding to each position"""

    # get length of alignment
    maxLength = max([len(seq) for seq in seqList])

    # initialize a data structure for storing the tallies
    dictList = [{} for i in xrange(maxLength)]

    for seq in seqList:
        #make sure seq is padded
        seqString = seq.seq
        seqString += '-'*(maxLength - len(seqString))

        # increment the dictionaries for this sequence
        # dict[char] = dict.get(char, 0) + 1
        # dict <--> dictList[i]
        # char <--> seqString[i]

        for i, c in enumerate(seqString):
            dictList[i][c] = dictList[i].get(c, 0) + 1

    return dictList

def consensus( tabdict, countGaps=False, plu=2, gap='-', errorchar='X', use_ambi=False ):
    """Given a dictionary from tabulate representing character frequencies
    at a single position, returns the most common char at
    that position subject to the rules below.

    countGaps       { 0 | 1 }
    plu            plurality for calling a consensus character

    Special cases:
    1) The most abundant character at a position is a gap
        if countGaps=0, uses the next most common character
            or 'x' if all chars are gaps
        if countGaps=1, puts a gap character ('-') at this position

    use_ambi - uses IUPAC ambiguity codes if possible in place of errorchar
    """


    tabdict = tabdict.copy()

    if not countGaps:
        try:
            del tabdict[gap]
        except KeyError:
            pass

        if len(tabdict) == 0:
            return errorchar

    # don't worry about gaps from here on
    if len(tabdict) == 1:
        return tabdict.keys()[0]

    rdict = dict([(v,k) for k,v in tabdict.items()])

    vals = sorted(tabdict.values())
    vals.reverse() #largest value is first

    majority, second = vals[:2]

    if majority-second < plu:
        if use_ambi:
            return IUPAC_rev.get(tuple(sorted(tabdict.keys())), errorchar)
        else:
            return errorchar
    else:
        return rdict[majority]

def count_subs(tabdict, countGaps=False, gap='-'):
    """Given a dict representing character frequency at a
    position of an alignment, returns 1 if more than
    one character is represented, 0 otherwise; excludes gaps
    if not countGaps. There must be at least minchars present for
    a position to be considered variable"""

    tabdict = tabdict.copy()

    if not countGaps:
        try:
            del tabdict[gap]
        except KeyError:
            pass

    if len(tabdict) <= 1:
        return 0

    # calculate count of most frequent character
    vals = sorted(tabdict.values())
    total = sum(vals)
    majority_char_count = vals.pop(-1)

    substitutions = total - majority_char_count

    return substitutions

def seqdiff(seq, templateseq, simchar='.'):
    """Compares seq and templateseq (can be Seq objects or strings) and returns
a string in which characters in seq that are identical
at that position to templateseq are replaced with simchar. Return object is the
length of the shorter of seq and templateseq"""

    seqstr = seq[:].upper()
    templatestr = templateseq[:].upper()

    lout = []
    for s,t in zip(seqstr, templatestr):
        if s == t:
            lout.append(simchar)
        else:
            lout.append(s)

    return ''.join(lout)

def get_vnumbers(seqstr, ignore_gaps=True, leadingZeros=True):

    seqlen = len(seqstr)

    digs = len(`seqlen+1`)
    if leadingZeros:
        fstr = '%%0%si' % digs
    else:
        fstr = '%%%ss' % digs

    gapstr = '-'*digs

    numchars = []
    i = 1
    for c in seqstr:
        if not ignore_gaps and c == '-':
            numchars.append(gapstr)
        else:
            numchars.append(fstr % i)
            i += 1

    if ignore_gaps:
        assert numchars == [fstr % x for x in xrange(1,seqlen+1)]

    return [''.join([x[i] for x in numchars]) for i in range(digs)]

def reformat_alignment(seqlist,
                       max_name_width=35,
                       seq_width=70,
                       include_consensus=True,
                       diff='consensus',
                       exclude_invariant=False,
                       min_subs=0,
                       seqs_per_page=65,
                       simchar='.',
                       number_by='consensus',
                       countGaps=False,
                       leadingZeros=True,
                       case=None):

    """
    Reformat an alignment of sequences for display.
    * diff - may take the following values:
      - 'consensus' - (default) each position in each sequence compared to
         corresponding position in consensus and replaced with simchar
      - [seq_name] - compare each sequence to sequence with name = seq_name
      - None - make no character replacements
    * number_by - sequence according to which numbering should be calculated
    * countGaps - do not exclude gaps in tabulation of columns to display
    * leadingZeros - include leading zeros in position numbers displayed on top line
      when exclude_invariant==True.
    * case - None (to change to input), 'upper' (force all to uppercase), 
      'lower' (force all to lowercase)
    """

    min_name_width = 10

    # avoid making modifications to input seqlist object in place
    seqlist = copy.deepcopy(seqlist)

    # make a dictionary of seq names
    seqdict = dict([(s.name,s) for s in seqlist])

    # a list of dicts
    tabulated = tabulate(seqlist)

    consensus_str = ''.join([consensus(d, countGaps=False) for d in tabulated])
    cons_seq = Seq.Seq('CONSENSUS', consensus_str)
    
    if case == 'upper':
        for seq in seqlist:
            seq.seq = seq.seq.upper()
    elif case == 'lower':
        for seq in seqlist:
            seq.seq = seq.seq.lower()
    
    if diff == 'consensus':
        for seq in seqlist:
            seq.seq = seqdiff(seq, consensus_str, simchar)
    elif diff is not None:
        try:
            # make a copy of the sequence to avoid modifying template seq below
            seq_to_diff = seqdict[diff][:]
        except KeyError:
            raise ValueError, 'Error: the sequence name provided for the diff argument (%s) is not found' % diff
        else:
            for seq in seqlist:
                seq.seq = seqdiff(seq, seq_to_diff, simchar)

    if number_by != 'consensus':
        try:
            vnumbers = get_vnumbers(seqdict[number_by][:], ignore_gaps=False, leadingZeros=leadingZeros)
        except KeyError:
            raise ValueError, 'Error: the sequence name provided for the number_by argument (%s) is not found' % number_by
        vnumstrs = vnumbers

    if exclude_invariant:
        compare = lambda d: count_subs(d, countGaps=countGaps) >= min_subs
        mask = [compare(d) for d in tabulated]
        apply_mask = lambda instr: ''.join(c for c,m in zip(instr, mask) if m)

        for seq in seqlist:
            seq.seq = apply_mask(seq)

        cons_seq.seq = apply_mask(cons_seq)

        if number_by == 'consensus':
            vnumbers = get_vnumbers(consensus_str, leadingZeros=leadingZeros)

        vnumstrs = [apply_mask(s) for s in vnumbers]

    name_width = min([max_name_width, max([len(s.name) for s in seqlist])])
    name_width = max([min_name_width, name_width])

    seqlen = len(seqlist[0])
    fstr = '%%(name)%(name_width)ss %%(seqstr)-%(seq_width)ss' % locals()

    seqcount = len(seqlist)

    out = []
    for start in range(0, seqlen, seq_width):
        stop = min([start + seq_width, seqlen])

        for first in xrange(0, seqcount, seqs_per_page):
            out.append([])
            last = min([first + seqs_per_page, seqcount])

            msg = ''
            if seqcount > seqs_per_page:
                msg += 'sequences %s to %s of %s' % \
                (first+1, last, seqcount)

            if number_by != 'consensus':
                msg += (' alignment numbered according to %s' % number_by)

            if msg:
                out[-1].append(msg)

            this_seqlist = seqlist[first:last]

            if exclude_invariant or number_by != 'consensus':
                # label each position
                for s in vnumstrs:
                    out[-1].append(
                    fstr % {'name':'NUM','seqstr':s[start:stop]} )
            else:
                # label position at beginning and end of block
                half_seq_width = int((stop-start)/2)
                numstr = ' '*name_width + \
                    ' %%-%(half_seq_width)ss%%%(half_seq_width)ss\n' % locals()
                out[-1].append( numstr % (start + 1, stop) )

            for seq in this_seqlist:
                seqstr = seq[start:stop]
                name = seq.name[:name_width]
                out[-1].append( fstr % locals() )

            if include_consensus:
                seqstr = cons_seq[start:stop]
                name = cons_seq.name
                out[-1].append( fstr % locals() )

    return out

def encode_aln(instr, gapchar='-', self_check=False):
    """
    Given a string containing gap characters, returns a list of two-tuples
    (insertion point, gap length) that can be used to transform the
    ungapped string to the gapped input."""

    gap_exp = re.compile(r'[%s]+' % gapchar)
    coords = [(B, E-B) for B,E in [mObj.span() for mObj in gap_exp.finditer(instr)]]

    if self_check:
        assert instr == decode_aln(gap_exp.sub('',instr),coords,gapchar)

    return coords

def decode_aln(instr, coords, gapchar='-'):
    """
    Transforms instr to contain gap characters according to the two-tuples
    in coords (insertion point, gap length)
    """

    chars = list(instr)
    for start, length in coords:
        chars = chars[:start] + [gapchar]*length + chars[start:]

    return ''.join(chars)

def get_os_type():
    """
    Tries to guess the operating system type. Returns
    either 'POSIX' or 'WINDOWS'
    """

    try:
        import _winreg
    except ImportError:
        os_type = 'POSIX'
    else:
        os_type = 'WINDOWS'

    return os_type

def find_exec(cmd, path=None):
    """
    * cmd - name of the executable
    * path - directory name or a list of directories possibly
      containing the executable. Searches PATH environment variable
      if None
    """

    if path is None:
        path = os.environ['PATH'].split(':')
    elif not hasattr(path, '__iter__'):
        path = [path]

    for pth in path:
        executable = os.path.join(pth.strip(), cmd)        
        if os.access(executable, os.X_OK):
            return executable

    return None

def run_bat(cmds, name=None, path='.', run=True, cleanup=True):
    """Execute a series of commands as a windows batch file."""

    cwd = os.path.abspath(path)
    suffix = '.bat'

    if name:
        outfilename = os.path.join(path, name+suffix)
    else:
        outfilename = os.path.join(path, randomname()+suffix)

    log.info('writing %s' % outfilename)

    f = open(outfilename, 'w')
    for cmd in cmds:
        f.write(cmd.strip() + os.linesep)
    f.write(os.linesep)
    f.close()

    if run:
        log.info('running %s' % outfilename)
        exit_status = os.system('cmd /c "%s"' % outfilename)

    if exit_status == 0 and cleanup:
        os.remove(outfilename)


def test():
    import sys, pprint, os
    from io_clustal import readAlnStr

    #mdir,_ = os.path.split(__file__)
    #infile = os.path.join(mdir, 'testfiles', 'oscillo_F41669_top20.aln')
    infile = os.path.join('testfiles', 'oscillo_F41669_top20.aln')

    seqlist = readAlnStr(open(infile).read())
    seq = seqlist[0]

    print wrap(seq)

    for block in reformat_alignment(seqlist):
        for line in block:
            print line
        print

    for block in reformat_alignment(seqlist, exclude_invariant=True):
        for line in block:
            print line
        print
