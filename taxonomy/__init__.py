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
        
        log.info(cmd)
        self.con.execute(cmd)
        
        cmd = """
        CREATE INDEX taxon_id_index ON taxonomy(tax_id)
        """ 
        log.info(cmd)
        try:
            self.con.execute(cmd)
        except self.con.OperationalError, msg:
            log.error(msg)
        
    def column_names(self, table_name):
        cur = self.con.cursor()
        cur.execute('pragma table_info(%s)' % table_name)
        return [r['name'] for r in cur.fetchall()]
        
        
        