import sqlite3 as sqlite
import operator
from create import *

names_keys = 'tax_id tax_name unique class'.split()
nodes_keys = 'tax_id parent_id rank embl_code division_id'.split()
merged_keys = 'old_tax_id new_tax_id'.split()
source_keys = 'source_id source_name'.split()
# cut -f 3 -d '|' nodes.dmp | sort | uniq
# see http://biowarehouse.ai.sri.com/repos/enumerations-loader/data/enumeration_inserts.txt
tax_keys = """
no rank
root
superkingdom
kingdom
subkingdom
superphylum
phylum
subphylum
superclass
class
subclass
infraclass
superorder
order
suborder
parvorder
infraorder
superfamily
family
subfamily
tribe
subtribe
genus
subgenus
species group
species subgroup
species
subspecies
varietas
forma
"""

tax_keys = [k.strip().replace(' ','_') for k in tax_keys.splitlines() if k.strip()]

def insert_cmd(tablename, keys, or_clause=''):

    vals = ', '.join(':%s'%k for k in keys)
    keys = ', '.join('`%s`'%k for k in keys)

    cmd = """
    insert %(or_clause)s into %(tablename)s
        (%(keys)s)
    values
        (%(vals)s)
    """ % locals()

    return cmd

class Taxonomy(object):

    """
    Class providing an interface to a database containing a taxonomy.
    """

    def __init__(self, dbname):
        self.dbname = dbname

        self.con = sqlite.connect(dbname)
        self.con.row_factory = \
            lambda cursor, row: \
                dict((col[0],row[idx]) for idx, col in enumerate(cursor.description))
        self.con.text_factory = str

        field_defs = ',\n'.join('            `%s` TEXT' % k for k in tax_keys)

        cmd = """
        create table if not exists taxonomy
        (
            `tax_id` TEXT unique,
            `parent_id` TEXT,
%(field_defs)s
        )""" % locals()

        log.debug(cmd)
        self.con.execute(cmd)

        cmd = """
        CREATE INDEX taxon_id_index ON taxonomy(tax_id)
        """
        log.debug(cmd)
        try:
            self.con.execute(cmd)
        except self.con.OperationalError, msg:
            log.debug(msg)

    def column_names(self, table_name):
        cur = self.con.cursor()
        cur.execute('pragma table_info(%s)' % table_name)
        return [r['name'] for r in cur.fetchall()]

    def _get_node(self, tax_id):

        cmd = """
        select nodes.*, tax_name, source.*
        from nodes join names on nodes.tax_id = names.tax_id
        join source on nodes.source_id = source.source_id
        where names.is_primary = 1
        and nodes.tax_id = ?
        """

        result = self.con.cursor().execute(cmd, (tax_id,)).fetchone()

        if result and result['parent_id'] != result['tax_id']:
            return result
        else:
            return None

    def source_id(self, source_name, add=True):
        """
        Return source_id corresponding to source_name. If add=True,
        add new source if necessary; otherwise return None if source is
        unknown.
        """

        cur = self.con.cursor()

        # catch the error instead of using 'or ignore' to prevent incrementing of source_id
        if add:
            try:
                cur.execute('insert into source (source_name) values (?)', (source_name,))
            except sqlite.IntegrityError:
                pass

        cur.execute('select * from source where source_name = ?', (source_name,))

        try:
            source_id = cur.fetchone()['source_id']
        except TypeError:
            source_id = None

        return source_id

    def has_node(self, tax_id):
        cur = self.con.cursor()
        cur.execute('select * from nodes where tax_id = ?', (tax_id,))
        return bool(cur.fetchone())

    def add_node(self, tax_id, tax_name, parent_id, source_name='NCBI', rank=None,
        division_id = '0', embl_code=None, get_lineage=False):

        cur = self.con.cursor()
        source_id = self.source_id(source_name)

        # determine rank of the new node
        parent = self.lineage(parent_id)
        try:
            parent_rank_i = tax_keys.index(parent.rank)
        except ValueError:
            print tax_keys
            print parent.rank
            print(parent)

            raise

        if rank is None:
            rank = tax_keys[parent_rank_i + 1]
        else:
            try:
                rank_i = tax_keys.index(rank)
                assert rank_i > parent_rank_i
            except AssertionError:
                raise ValueError('rank of new child (%s) must be higher than rank of parent (%s)',
                    rank,
                    parent.rank)
            except IndexError:
                raise ValueError('rank "%s" is not known' % rank)

        # add to nodes table
        cmd = insert_cmd(tablename='nodes', keys=nodes_keys + ['source_id'],
            or_clause='or ignore')
        log.debug(cmd)
        cur.execute(cmd, locals())

        # is the name already in the names table?
        cur.execute('select * from names where tax_id = ?', (tax_id,))
        existing = cur.fetchall()
        is_primary = not bool(existing)

        if tax_name not in set([row['tax_name'] for row in existing]):
            # add to names table
            cmd = insert_cmd(tablename='names', keys=['tax_id','tax_name','is_primary'])
            log.debug(cmd)
            cur.execute(cmd, locals())

        self.con.commit()

        if get_lineage:
            return self.lineage(tax_id)
        else:
            return None


    def _get_lineage(self, tax_id, top_level=True):
        """
        Return a taxonomic lineage, adding absent lineages to table taxonomy.
        """

        tax_id = str(tax_id)

        if not tax_id:
            return {}

        cur = self.con.cursor()

        cur.execute('select * from taxonomy where tax_id = ?', (tax_id,))
        result = cur.fetchone()

        if result:
            log.debug( 'found %s' % tax_id)
            lineage = dict([(k,result[k]) for k in ['tax_id','parent_id'] + tax_keys if result[k]])
        else:
            orig_id = tax_id
            log.info( 'constructing lineage for %s' % tax_id)

            node_data = self._get_node(tax_id)
            if node_data:
                parent_id = node_data['parent_id']
                this_rank = node_data['rank'].replace(' ','_')
                log.debug("this_rank: %s    node_data['tax_id']: %s" % \
                (this_rank, node_data['tax_id']))

                # recursively get higher-level nodes
                parentdict = self._get_lineage(parent_id, top_level=False)

                taxdict = parentdict.copy()
                taxdict[this_rank] = node_data['tax_id']
            else:
                taxdict = {}
                parent_id = orig_id

            taxdict['tax_id'] = orig_id
            taxdict['parent_id'] = parent_id

            # add this data to the database
            cmd = insert_cmd(tablename='taxonomy', keys=taxdict.keys())
            log.debug(cmd)
            cur.execute(cmd, taxdict)

            lineage = taxdict
            if top_level:
                self.con.commit()

        return lineage

    def _get_tax_id(self, tax_name):

        cur = self.con.cursor()

        cur.execute('select tax_id from names where tax_name = ?', (tax_name,))
        result = cur.fetchone()

        return result and result.get('tax_id') or None

    def lineage(self, tax_id=None, tax_name=None):
        """
        Return an object of class Lineage for the given tax_id
        or tax_name
        """

        if not operator.xor(bool(tax_id),bool(tax_name)):
            raise ValueError('Exactly one of tax_id and tax_name must have a value.')

        if tax_name:
            tax_id = self._get_tax_id(tax_name)

            if not tax_id:
                raise ValueError('No lineage available for tax_name "%s"' % tax_name)

        lineage = self._get_lineage(tax_id)
        node = self._get_node(tax_id)

        if not node:
            raise ValueError('No lineage available for tax_id "%s"' % tax_id)

        # get names corresponding to tax_ids in lineage
        cmd = """
        select tax_name from names
        where tax_id = ?
        and is_primary = 1
        """
        namedict = {}
        for rank in tax_keys:
            if rank in lineage:
                tax_id = lineage[rank]
                namedict[tax_id] = self.con.cursor().execute(cmd, (tax_id,)).fetchone()['tax_name']

        return Lineage(lineage, node, namedict)


class Lineage(object):

    """
    Container class for a taxonomic lineage. Constructor is meant
    to be called by the Taxonomy class.
    """

    tax_keys = tax_keys
    _attribute_names = set(tax_keys + nodes_keys + source_keys + ['tax_name'])

    def __init__(self, lineage, node, namedict):

        self._data = lineage.copy()
        self._data.update(node)
        self._namedict = namedict
        self.tax_id = self._data['tax_id']
        self.parent_id = self._data['parent_id']
        # list of (rank, tax_id) tuples
        self.ranks = [(k,self._data.get(k)) for k in self.tax_keys]
        try:
            self.rank = [x[0] for x in self.ranks if x[1]][-1]
        except IndexError:
            self.rank = None

    def __getattr__(self, name):
        """
        Access object._data as instance attribute.
        """

        if name in self._attribute_names:
            return self._data.get(name, None)
        else:
            raise AttributeError

    def __getitem__(self, key):
        return getattr(self, key)

    def __eq__(self, other):
        """
        Compares equality of self._data to support == operator
        """

        return self._data == other._data


    def __str__(self):
        """
        Representation of object using print
        """
        lines = []
        lines.append('%20s * %s' % ('--- rank','taxon ---'))
        lines += [   '%20s - %s (%s)' % (k.rstrip('_'), self._namedict[self._data[k]], self._data[k]) for k in reversed(self.tax_keys) if k in self._data]
        lines.append('%20s * %s' % ('--- attribute','value ---'))
        lines += [   '%20s - %s' % (k,self._data[k]) for k in ['source_name','division_id','embl_code']]
        return '\n'.join(lines)

    def __repr__(self):
        """
        Representation of object using str()
        """

        return '<%(rank)s: %(tax_name)s (tax_id %(tax_id)s)>' % self

    def get_name(self, rank=None):
        """
        Return tax_name corresponding to tax_id at rank or to
        self.tax_id if rank is not provided.
        """

        if rank:
            return self._namedict.get(self[rank])
        else:
            return self._namedict.get(self.tax_id)

