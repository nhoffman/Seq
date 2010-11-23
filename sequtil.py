import re
import copy
import random
import string
import Seq
import os
import logging
import math
import itertools

import time
import operator

try:
    import pp
except ImportError:
    pp_ok = False
else:
    pp_ok = True

from itertools import izip, chain, repeat, islice, takewhile

try:
    from itertools import izip_longest
except ImportError:
    def izip_longest(*args, **kwds):
        # see http://docs.python.org/library/itertools.html#recipes
        # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
        fillvalue = kwds.get('fillvalue')
        def sentinel(counter = ([fillvalue]*(len(args)-1)).pop):
            yield counter()         # yields the fillvalue, or raises IndexError
        fillers = repeat(fillvalue)
        iters = [chain(it, sentinel(), fillers) for it in args]
        try:
            for tup in izip(*iters):
                yield tup
        except IndexError:
            pass


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
                       case=None,
                       seqrange=None):

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
    * seqrange - optional two-tuple specifying start and ending coordinates (0-index)

    """

    min_name_width = 10

    # avoid making modifications to input seqlist object in place
    seqlist = copy.deepcopy(seqlist)

    # make a dictionary of seq names
    seqdict = dict([(s.name,s) for s in seqlist])

    # a list of dicts
    tabulated = tabulate(seqlist)

    consensus_str = ''.join([consensus(d, countGaps=countGaps) for d in tabulated])
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
            vnumbers = get_vnumbers(seqdict[number_by][:], ignore_gaps=countGaps, leadingZeros=leadingZeros)
        except KeyError:
            raise ValueError, 'Error: the sequence name provided for the number_by argument (%s) is not found' % number_by
        vnumstrs = vnumbers

    # we use a mask to define columns to include in the output
    if exclude_invariant:
        compare = lambda d: count_subs(d, countGaps=countGaps) >= min_subs
        mask = [compare(d) for d in tabulated]

        if seqrange:
            rr = range(*seqrange)
            mask = [m and i in rr for i,m in enumerate(mask)]

        apply_mask = lambda instr: ''.join(c for c,m in zip(instr, mask) if m)

        for seq in seqlist:
            seq.seq = apply_mask(seq)

        cons_seq.seq = apply_mask(cons_seq)

        if number_by == 'consensus':
            vnumbers = get_vnumbers(consensus_str, leadingZeros=leadingZeros)

        vnumstrs = [apply_mask(s) for s in vnumbers]

    name_width = min([max_name_width, max([len(s.name) for s in seqlist])])
    name_width = max([min_name_width, name_width])

    fstr = '%%(name)%(name_width)ss %%(seqstr)-%(seq_width)ss' % locals()

    seqcount = len(seqlist)
    align_start, align_stop = 0, len(seqlist[0])

    out = []
    for start in range(align_start, align_stop, seq_width):
        stop = min([start + seq_width, align_stop])

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

def reformat(seqs,
             name_min = 10,
             name_max = 35, #
             nrow = 65, #
             ncol = 70, #
             add_consensus = True, #
             compare_to = -1, #
             exclude_gapcols = True, #
             exclude_invariant = False, #
             min_subs = 1, #
             simchar = '.',
             number_by = 0, #
             countGaps = True,
             case = None, #
             seqrange = None,
             seqnums = False
             ):

    """
    Reformat an alignment of sequences for display. Return a list of
    lists of strings; the outer list corresponds to pages.

    * seqs - list of Seq objects
    * name_min - minimum number of characters to allot to sequence names
    * name_max - maximum number of characters to allot to sequence names
    * nrow - number of lines per page
    * ncol - width in characters of sequence on each line
    * add_consensus - If True, include consensus sequence.
    * compare_to - may take the following values:
      - 0 - (default) each position in each sequence compared to
         corresponding position in consensus and replaced with simchar
      - 1 <= i <= len(seqlist) - compare each sequence to sequence at index (i - 1)
      - -1 - make no character replacements
    * exclude_gapcols - if True, mask columns with no non-gap characters
    * exclude_invariant - if True, mask columns without minimal polymorphism
    * min_subs -
    * simchar - character indicating identity to corresponding position in compare_to
    * number_by - sequence (1-index) according to which numbering should be calculated
      or 0 for the consensus.
    * countGaps - include gaps in calculation of consensus and columns to display
    * case - None (to change to input), 'upper' (force all to uppercase),
      'lower' (force all to lowercase)
    * seqrange - optional two-tuple specifying start and ending coordinates (1-index, inclusive)
    * seqnums - show sequence numbers (1-index) to left of name if True
    """

    name_min = 10

    # avoid making modifications to input seqlist object in place
    seqlist = copy.deepcopy(seqs)
    seqnames = [seq.name for seq in seqs]
    nseqs = len(seqlist)

    # make a dictionary of seq names
    seqdict = dict([(s.name,s) for s in seqlist])

    # a list of dicts
    tabulated = tabulate(seqlist)

    consensus_str = ''.join([consensus(d, countGaps=countGaps) for d in tabulated])
    consensus_name = 'CONSENSUS'
    if add_consensus:
        seqlist.append(Seq.Seq(consensus_name, consensus_str[:]))

    # change case if requested.
    if case:
        for seq in seqlist:
            seq.seq = getattr(seq.seq, case)()

    # for compare_to and number_by, make a copy of the sequence for
    # comparison because the original sequences will be modified
    if compare_to >= 0:
        try:
            seq_to_compare_to = consensus_str \
                if compare_to == 0 \
                else seqlist[compare_to - 1][:]
        except IndexError:
            raise ValueError('Error in compare_to="%s": index out of range.' % compare_to)

        for i, seq in enumerate(seqlist): # don't modify reference sequence
            if (compare_to == 0 and seq.name == consensus_name) or compare_to == i + 1:
                # if re.match(r'^%s$' % compare_to, seq.name, re.I):
                seq.name = '-ref-> ' + seq.name
            else:
                seq.seq = seqdiff(seq, seq_to_compare_to, simchar)

    ii = range(len(seqlist[0]))
    # show columns where mask is True
    mask = [True for i in ii]
    if seqrange:
        start, stop = seqrange
        mask = [start <= i+1 <= stop for i in ii]

    if exclude_gapcols:
        mask1 = [d.get('-',0) != nseqs for d in tabulated]
        mask = [m and m1 for m,m1 in zip(mask, mask1)]

    if exclude_invariant:
        mask1 = [count_subs(d, countGaps=countGaps) >= min_subs for d in tabulated]
        mask = [m and m1 for m,m1 in zip(mask, mask1)]

    if seqrange or exclude_invariant or exclude_gapcols:
        apply_mask = lambda instr: ''.join(c for c,m in zip(instr, mask) if m)

        for seq in seqlist:
            seq.seq = apply_mask(seq)

        try:
            number_by_str = consensus_str if number_by == 0 else seqlist[number_by - 1][:]
            number_by_name = consensus_name if number_by == 0 else seqnames[number_by - 1][:]
        except IndexError:
            raise ValueError('Error in number_by="%s": index out of range.' % number_by)

        vnumstrs = [apply_mask(s) for s in get_vnumbers(number_by_str, leadingZeros=True)]

    seqcount = len(seqlist)

    longest_name = max([len(s.name) for s in seqlist])
    name_width = max([name_min, min([longest_name, name_max])])

    num_width = math.floor(math.log10(seqcount)) + 1

    fstr = '%%(name)%(name_width)ss %%(seqstr)-%(ncol)ss' % locals()
    if seqnums:
        fstr = ('%%(count)%(num_width)is ' % locals()) + fstr

    colstop = len(seqlist[0])

    out = []
    # start is leftmost column for each block of columns
    for start in xrange(0, colstop, ncol):
        stop = min([start + ncol, colstop])

        # breaks into vertical blocks of sequences
        counter = itertools.count(1)
        for first in xrange(0, seqcount, nrow):
            out.append([])
            last = min([first + nrow, seqcount])

            msg = ''
            if seqcount > nrow:
                msg += 'sequences %s to %s of %s' % \
                (first+1, last, seqcount)

            if number_by != 0:
                msg += (' alignment numbered according to %s' % number_by_name)

            if msg:
                out[-1].append(msg)

            this_seqlist = seqlist[first:last]

            if exclude_invariant or exclude_gapcols or number_by > 0:
                # label each position
                for s in vnumstrs:
                    out[-1].append(
                    fstr % {'count':'','name':'#','seqstr':s[start:stop]} )
            else:
                # label position at beginning and end of block
                half_ncol = int((stop-start)/2)
                numstr = '#'+' '*name_width + \
                    ' %%-%(half_ncol)ss%%%(half_ncol)ss\n' % locals()
                out[-1].append( numstr % (start + 1, stop) )

            for seq in this_seqlist:
                count = counter.next()
                seqstr = seq[start:stop]
                name = seq.name[:name_width]
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


######## functions used in findDuplicates.py
def grouper(n, iterable, pad=True):
    """
    Return sequence of n-tuples composed of successive elements
    of iterable; last tuple is padded with None if necessary. Not safe
    for iterables with None elements.
    """

    args = [iter(iterable)] * n
    iterout = izip_longest(fillvalue=None, *args)

    if pad:
        return iterout
    else:
        return (takewhile(lambda x: x is not None, c) for c in iterout)

def flatten(d):
    return sorted(d.keys() + list(chain(*d.values())))

#### the real work is done in coalesce and merge

def coalesce(strings, comp='contains', log=log):

    """
    Groups a collection of strings by identifying the longest string
    representing each nested set of substrings (if comp='contains') or
    into sets of identical strings (if comp='eq')

    Input
    =====

     * strings - a tuple of N strings
     * comp - 'contains' (default) or 'eq'
     * log - a logging object; defualt is the root logger

     Output
     ======

     * a dict keyed by indices in strings. Each key i returns a list of
       indices corresponding to strings nested within (or identical to) the
       string at strings[i].
    """

    start = time.time()

    idx = range(len(strings))

    if __debug__:
        idx_orig = idx[:]

    # sort idx by length, descending
    idx.sort(key=lambda i: len(strings[i]),reverse=True)
    log.debug('sort completed at %s secs' % (time.time()-start))
    nstrings = len(idx)

    d = dict((i,list()) for i in idx)

    # operator.eq(a,b) <==> a == b
    # operator.contains(a,b) <==> b in a
    compfun = getattr(operator, comp)

    cycle = 0
    while len(idx) > 0:
        parent_i = idx.pop(0)
        parent_str = strings[parent_i]
        if __debug__: # suppress using python -O
            cycle += 1
            log.debug('cycle %3s i=%-5s length = %-4s %5s remaining' % \
                (cycle,
                 parent_i,
                 len(strings[parent_i]),
                 len(idx)
                 ))

        children = set(i for i in idx if compfun(parent_str,strings[i]))
        d[parent_i].extend(children)
        idx = [x for x in idx if x not in children]

    for i in chain(*d.values()):
        del d[i]

    log.info('Coalesce %s strings to %s in %.2f secs' % (nstrings, len(d), time.time()-start))

    if __debug__:
        dFlat = flatten(d)
        log.debug('checking d of length %s with min,max=%s,%s' % \
            (len(d), min(dFlat), max(dFlat)))

        assert set(idx_orig) == set(dFlat)

        for parent, children in d.items():
            for child in children:
                assert strings[child] in strings[parent]

    return d

def merge(strings, d1, d2=None, comp='contains'):

    """
    Merge two dictionaries mapping superstrings to substrings.

    Input
    =====

     * strings - a tuple of N strings
     * d1, d2 - output of coalesce()
     * comp - type of string comparison, passed to coalesce ("contains" or "eq")

    Output
    ======

     * a single dict mapping superstrings to substrings

    """

    if d2 is None:
        log.warning('d2 not provided, returning d1')
        return d1

    d = coalesce(strings, idx=d1.keys()+d2.keys(), comp=comp)

    for i, dvals in d.items():
        if dvals:
            d[i].extend(list(chain(*[d1.get(j,[]) for j in dvals])))
            d[i].extend(list(chain(*[d2.get(j,[]) for j in dvals])))
        d[i].extend(d1.get(i,[]))
        d[i].extend(d2.get(i,[]))

    if __debug__:
        d1Flat, d2Flat, dFlat = flatten(d1), flatten(d2), flatten(d)
        log.info('checking d of length %s with min,max=%s,%s' % \
            (len(d),min(dFlat),max(dFlat)))

        assert set(d1Flat + d2Flat) == set(dFlat)

        for parent, children in d.items():
            for child in children:
                assert strings[child] in strings[parent]


    return d

def split_and_merge(strings, comp='contains', chunksize=None):

    """
    Given a sequence of strings, return a dictionary mapping
    superstrings to substrings.

    Input
    =====

     * strings - a tuple of N strings
     * comp - defines string comparison method: 'contains' -> "s1 in s2" or
       'eq' -> "s1 == s2"
     * chunksize - an integer defining size of partitions into which
       strings are divided; each partition is coalesced individually, and the
       results of each are merged.

    Output
    ======

     * A dict mapping superrstrings to substrings, in which keys and
     values are indices in strings.

    """

    nstrings = len(strings)

    if not chunksize:
        chunksize = nstrings

    ### the important stuff happens from here...
    chunks = grouper(n=chunksize, iterable=xrange(nstrings), pad=False)
    # TODO: parallelize me
    coalesced = [coalesce(strings, c, comp=comp) for c in chunks]

    cycle = 1
    while len(coalesced) > 1:
        log.warning('merge cycle %s, %s chunks' % (cycle,len(coalesced)))
        # TODO: parallelize me
        coalesced = [merge(strings, d1, d2, comp=comp) for d1,d2 in grouper(n=2, iterable=coalesced)]
        cycle += 1

    d = coalesced[0]
    ### ... to here

    assert set(flatten(d)) == set(range(nstrings))

    return d

