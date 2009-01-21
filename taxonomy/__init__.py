import sqlite3 as sqlite
from create import *

names_keys = 'tax_id name unique class'.split()
nodes_keys = 'tax_id parent_id rank embl_code division_id'.split()
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

class Taxonomy:

    def __init__(self, dbname):
        self.dbname = dbname
        
        self.con = sqlite.connect(dbname)
        self.con.row_factory = lambda cursor, row: dict((col[0],row[idx]) for idx, col in enumerate(cursor.description))
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

    def get_node(self, tax_id):
                
#         cmd = """
#         select tax_id, parent_id, rank, 
#         (select tax_name from names 
#         where tax_id = %(tax_id)s
#         and is_primary = 1) as tax_name
#         from nodes 
#         where tax_id = %(tax_id)s
#         """ % locals()
        
        cmd = """
        select nodes.tax_id, parent_id, rank, tax_name
        from nodes join names on nodes.tax_id = names.tax_id
        where names.is_primary = 1
        and nodes.tax_id = ?
        """
        
        result = self.con.cursor().execute(cmd, (tax_id,)).fetchone()
        
        if result and result['parent_id'] != result['tax_id']:
            return result
        else:
            return None

    def get_lineage(self, tax_id):
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
            return dict([(k,result[k]) for k in ['tax_id','parent_id'] + tax_keys if result[k]]) 
        else:
            log.info( 'constructing lineage for %s' % tax_id)
            orig_id = tax_id
            log.debug( '    constructing taxonomy for %s' % tax_id)
            
            node_data = self.get_node(tax_id)
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
                parentdict = self.get_lineage(parent_id)            
                            
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
        
        