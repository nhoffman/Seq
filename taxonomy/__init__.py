import sqlite3 as sqlite
import operator
from create import *

names_keys = 'tax_id tax_name unique class'.split()
nodes_keys = 'tax_id parent_id rank embl_code division_id'.split()
source_keys = 'source_id source_name'.split()
# cut -f 3 -d '|' nodes.dmp | sort | uniq  
# see http://biowarehouse.ai.sri.com/repos/enumerations-loader/data/enumeration_inserts.txt
tax_keys = """
no rank
root
superkingdom
kingdom
superphylum
phylum
subphylum
superclass
class
subclass
infraclass
superorder
order_
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
    
class Taxonomy:

    def __init__(self, dbname):
        self.dbname = dbname
        
        self.con = sqlite.connect(dbname)
        self.con.row_factory = \
            lambda cursor, row: \
                dict((col[0],row[idx]) for idx, col in enumerate(cursor.description))
        self.con.text_factory = str
        
        field_defs = ',\n'.join('    %-25s TEXT' % k for k in tax_keys)
        
        cmd = """
        create table if not exists taxonomy
        (
            tax_id       TEXT unique,
            parent_id    TEXT,
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
    
    def add_node(self, tax_id, tax_name, parent_id, source_name='NCBI', rank=None,
        division_id = '0', embl_code=None):
        
        cur = self.con.cursor()
                
        # make sure source is known
        
        # catch the error instead of using 'or ignore' to prevent incrementing of source_id
        try:
            cur.execute('insert into source (source_name) values (?)', (source_name,))
        except sqlite.IntegrityError:
            pass
        cur.execute('select * from source where source_name = ?', (source_name,))
        source_id = cur.fetchone()['source_id']
                
        # determine rank of the new node
        parent = self.lineage(parent_id)
        parent_rank_i = tax_keys.index(parent.rank)
        if rank is None:
            rank = tax_keys[parent_rank_i + 1]
        else:
            try:
                rank_i = tax.keys.index(rank)
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
        log.info(cmd)
        cur.execute(cmd, locals())

        # is the name already in the names table?
        cur.execute('select * from names where tax_id = ?', (tax_id,))
        existing = cur.fetchall()
        is_primary = not bool(existing)
                
        if tax_name not in set([row['tax_name'] for row in existing]):
            # add to names table        
            cmd = insert_cmd(tablename='names', keys=['tax_id','tax_name','is_primary'])
            log.info(cmd)
            cur.execute(cmd, locals())
        
        self.con.commit()
            
    def _get_lineage(self, tax_id):
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
            log.info( 'found %s' % tax_id)
            lineage = dict([(k,result[k]) for k in ['tax_id','parent_id'] + tax_keys if result[k]]) 
        else:
            orig_id = tax_id
            log.debug( '    constructing lineage for %s' % tax_id)
            
            node_data = self._get_node(tax_id)
            if node_data:
                parent_id = node_data['parent_id']
                            
                this_rank = node_data['rank']
                if this_rank == 'order':
                    this_rank = 'order_'
                else:
                    this_rank = this_rank.replace(' ','_')
                            
                log.debug("this_rank: %s    node_data['tax_name']: %s" % \
                (this_rank, node_data['tax_name']))
        
                # recursively get higher-level nodes
                parentdict = self._get_lineage(parent_id)            
                            
                taxdict = parentdict.copy()
                taxdict[this_rank] = node_data['tax_name']
            else:
                taxdict = {}
                parent_id = orig_id
            
            taxdict['tax_id'] = orig_id
            taxdict['parent_id'] = parent_id
            
            # add this data to the database             
            fields, tax_data = zip(*taxdict.items())
                    
            fieldstr = ', '.join(fields)
            qmarks = ', '.join(['?']*len(tax_data))
                    
            cmd = """
            insert into taxonomy 
            (%(fieldstr)s)
            values
            (%(qmarks)s)""" % locals()
            
            cur.execute(cmd, tax_data)
            
            lineage = taxdict
        
        return lineage

    def lineage(self, tax_id):
        """
        Return an object of class Lineage for the given tax_id
        """
        
        lineage = self._get_lineage(tax_id)
        node = self._get_node(tax_id)
        
        return Lineage(lineage, node)

        
class Lineage(object):
    
    tax_keys = tax_keys
    _attribute_names = set(tax_keys + nodes_keys + source_keys + ['tax_name'])
    
    def __init__(self, lineage, node):
        
        self._data = lineage.copy()
        self._data.update(node)
        self.tax_id = self._data['tax_id']
        self.parent_id = self._data['parent_id']
        
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
        
    def __str__(self):
        """
        Representation of object using print
        """
                    
        fstr = '%20s - %s'
        lines = ['%(rank)s: %(tax_name)s (tax_id %(tax_id)s)' % self]
        lines.append(fstr % ('--- rank','tax_name ---'))
        lines += [fstr % (k.rstrip('_'),self._data[k]) for k in self.tax_keys if k in self._data]
        lines.append(fstr % ('--- attribute','value ---'))
        lines += [fstr % (k,self._data[k]) for k in ['source_name','division_id','embl_code']]
        return '\n'.join(lines)

    def __repr__(self):
        """
        Representation of object using str()
        """
        
        return '<%(rank)s: %(tax_name)s (tax_id %(tax_id)s)>' % self

        
        