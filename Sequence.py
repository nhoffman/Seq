"""
Defines the Sequence object. Contains a nucleotide sequence plus information such as name,
a header string, accession number.
"""

from sequtil import wrap

__version__ = '$Id$'

class Seq(object):
    """
    The Sequence class"""

    def __init__( self, name, seq, hea=None, data=None, **kwargs):
        """
        name      name of sequene
        seq       sequence
        [hea]     header information
        [data]    a dict containing arbitrary data; initialized to
                  contain the 'hea' key

        !!!!! ALL INDEXING IN THIS CLASS IS 0-BASED - EXCEPT getSeq1() !!!!!
        """

        self.name = name
        self.seq = seq

        if hea:
            self.hea = hea
        else:
            self.hea = ''

        self.keys = ['name','seq','hea']

        for k,v in kwargs.items():
            self.keys.append(k)
            setattr(self, k, v)


    def __repr__( self ):
        """Special method to return string representation of the
        whole sequence object when `obj` or repr(obj) is called"""

        return """>%s%s\n%s""" % (self.name, self.hea, wrap(self.seq, 60))


    def __str__( self ):
        """Special method to return sequence string when str(obj)
        is called"""
        return self.seq

    def __eq__( self, other ):
        """Special method executed when a sequence objects is compared
        to self; returns 1 if sequences are idential (irrespective of case) and 0
        otherwise; does not take into account name or other fields. If other
        is a string, compares to self.seq"""

        try:
            return self.seq.upper() == other.seq.upper()
        except AttributeError:
            return self.seq.upper() == other.upper()

    def __len__( self ):
        """Special method execued when len( obj ) is called; returns length of
        sequence"""

        return len( self.seq )

    def __getitem__( self, index ):
        """Special method to obtain single elements from sequence string
        by calling obj[key];
        !!!!! INDEXES ARE 0-BASED !!!!!"""

        return self.seq[index]


    def __getslice__( self, start, end ):
        """Special method to obtain object slices as in obj[i:j]
        !!!!! INDEXES ARE 0-BASED !!!!!
        """

        return self.seq[start:end]

    def __contains__( self, substring ):
        """Special method called when 'item in obj' is executed; returns 0 or 1
        """

        found = self.seq.upper().find( substring.upper() )
        if found == -1:
            found = 0
        else:
            found = 1
        return found

    def __add__( self, seqObj ):
        """Special method to concatenate two sequence objects. All properties
        of the leftmost Seq object are retained. """

        newStr = self.seq + seqObj.getSeq()
        return Seq( name=self.name, seq=newStr, data=self.data )

    def __call__( self ):
        """Special method executed when obj() is called; returns the sequence
        string"""

        return self.seq

    def getSeq1( self, start, end ):
        """Return sequence string from 1-based index |start|
        to 1-based index |end|, both inclusive; only
        positive indexes allowed"""

        if start <= 0 or end <= 0:
            raise IndexError, "Zero or negative index"

        start = start - 1
        return self.seq[ start:end ]
