import os
import logging
import urllib
import zipfile
import stat
import pprint
import sqlite3 as sqlite

from __init__ import names_keys, nodes_keys

log = logging

def get_ncbi_tax_data(dest_dir='.', expand=['nodes.dmp','names.dmp','readme.txt'], new=False):
    """
    Download data from NCBI required to generate local
    taxonomy database from url
    ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdmp.zip
    
    see ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump_readme.txt
    """
    
    dest_dir = os.path.abspath(dest_dir)
    try:
        os.mkdir(dest_dir)
    except OSError:
        pass
    
    url = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdmp.zip'
    fout = os.path.join(dest_dir, os.path.split(url)[-1])
            
    if os.access(fout, os.F_OK) and not new:
        log.info('%s exists; not downloading' % fout)
    else:   
        # get the file
        log.warning('downloading %(fout)s to %(dest_dir)s' % locals())
        urllib.urlretrieve(url, fout)
    
    zfile = zipfile.ZipFile(fout, 'r')
    log.info('contents of %s: \n%s' % (fout, pprint.pformat(zfile.namelist()) ))
    
    outfiles = {}
    for arcname in expand:   
        
        destfile = os.path.join(dest_dir, arcname)
        outfiles[arcname.rstrip('.dmp')] = destfile
        
        if not os.access(destfile, os.F_OK) and not new:
            log.info('expanding %s' % arcname)
            open(destfile,'wb').write(zfile.read(arcname))
        
        mb = 1024*1024
        file_size = '%i mb' % ((os.stat(destfile)[stat.ST_SIZE])/mb) # convert to kb
        log.info('%s: %s' % (destfile, file_size))
    
    return outfiles

def read_dmp(infile, keys, condition=None):
    """Condition is a function that accepts a rowdict - returns True if 
    the row should be kept. All rows will be accepted by default.
    """
        
    if condition is None:
        condition = lambda rowdict: True
        
    for i, line in enumerate(open(infile,'rU')):        
        splitline = line.rstrip('\t|\n').split('\t|\t')
        rowdict = dict(zip(keys, splitline))
        
        if condition(rowdict):
            yield rowdict
        else:
            continue

def _is_primary_name(rowdict):
    
    if rowdict['class'] != 'scientific name':
        return False

    if rowdict['unique'] == '' or rowdict['name'] == rowdict['unique'].split('<')[0].strip():
        return True

    return False

def _bact_nodes_condition(rowdict):

#     Divisions (from division.dmp)    
#     0       |       BCT     |       Bacteria        |               |
#     1       |       INV     |       Invertebrates   |               |
#     2       |       MAM     |       Mammals |               |
#     3       |       PHG     |       Phages  |               |
#     4       |       PLN     |       Plants  |               |
#     5       |       PRI     |       Primates        |               |
#     6       |       ROD     |       Rodents |               |
#     7       |       SYN     |       Synthetic       |               |
#     8       |       UNA     |       Unassigned      |       No species nodes should inherit this division assignment        |
#     9       |       VRL     |       Viruses |               |
#     10      |       VRT     |       Vertebrates     |               |
#     11      |       ENV     |       Environmental samples   |       Anonymous sequences cloned directly from the environment        |    

#    TODO: What is the appropriate set of divisions to include?   
     
    ok_divs = set(['0','4','8'])
    return (rowdict['division_id'] in ok_divs) or (rowdict['rank'] == 'superkingdom')

def read_bacterial_taxonomy(names, nodes, primary_only=True, **args):
    """
    Parses names.dmp and nodes.dmp, filtering contents to retain data
    required to construct the bacterial NCBI taxonomy.
    
    * names - path to names.dmp
    * nodes - path to nodes.dmp
    * primary_only - if True, skip all but primary taxon names (ie, omit synonyms)
    
    Returns tuple of iterators (names_data, nodes_data)
    """
    
    if primary_only:
        condition = _is_primary_name
    else:
        condition = None

    names_data = read_dmp(infile=names, keys=names_keys, condition=condition)
    nodes_data = read_dmp(infile=nodes, keys=nodes_keys, condition=_bact_nodes_condition)
    
    return (names_data, nodes_data)
    
def make_nodes_db(con, data, keys=nodes_keys):
    
    typedict = {} # specify data type by field name here
            
    fields = [(k, typedict.get(k,'TEXT')) for k in keys]
    fieldcmds = ',\n'.join('    %-25s %s' % t for t in fields)
    keylist = ', '.join(keys)
    qmarks = ', '.join(['?']*len(keys))
    
    cmd = """
create table nodes
(
%(fieldcmds)s)
""".strip() % locals()
    log.info(cmd)
    con.execute(cmd)
    
    cmd = """CREATE INDEX nodes_id_index ON nodes(tax_id)"""
    log.info(cmd)
    con.execute(cmd)
    
    cmd = """
insert into nodes
    (%(keylist)s)
values
    (%(qmarks)s)""".strip() % locals()
    
    log.info(cmd)
    
    con.executemany(
        cmd, 
        (tuple([row[k] for k in keys]) for row in data)
    )
    con.commit()

def make_names_db(con, data):
    
    cmds = []
    cmds.append("""
CREATE TABLE names 
(
tax_id TEXT,
tax_name TEXT,
is_primary INTEGER
)""")
    cmds.append("""CREATE INDEX tax_name_i ON names (tax_name)""")
    cmds.append("""CREATE INDEX tax_id_i ON names (tax_id)""")
    cmds.append("""CREATE INDEX is_primary_i ON names (is_primary)""")
    
    for cmd in cmds:
        log.info(cmd)
        con.execute(cmd)
        
    cmd = """
insert into names
    (tax_id, tax_name, is_primary)
values
    (?, ?, ?)""".strip()
    
    log.info(cmd)
        
    con.executemany(
        cmd, 
        ( (row['tax_id'], row['name'], int(_is_primary_name(row))) for row in data )
    )
    con.commit()
    
def create_bacterial_taxonomy_db(names_data, nodes_data, dbname='ncbi_bact_taxonomy.db', 
    dest_dir='.', new=True):
        
    dbname = os.path.join(dest_dir, dbname)
    
    if new:
        try:
            os.remove(dbname)
        except OSError:
            pass
    
    con = sqlite.connect(dbname)
    make_nodes_db(con, nodes_data)
    make_names_db(con, names_data)    
    con.close()
    return dbname
    