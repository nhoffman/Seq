def get_node(conn, tax_id):
        
    cmd = """select tax_id, parent_id, rank, 
            (select tax_name from names 
            where tax_id = %(tax_id)s
            and valid = 1) as tax_name
        from nodes 
        where tax_id = %(tax_id)s
        """ % locals()

    result = conn.fetchone(cmd)
    
    if result and result['parent_id'] != result['tax_id']:
        return result
    else:
        return None
        
def get_taxonomy(conn, tax_id):
    """
    Return a taxonomic lineage, adding absent lineages to table taxonomy.
    """
    
    if not tax_id:
        return {}
    
    field_defs = ',\n'.join('    %-25s TEXT' % k for k in tax_keys)
    
    cmd = """
    create table if not exists taxonomy
    (
        tax_id       INTEGER primary key,
        parent_id    INTEGER,
        %(field_defs)s
    )""" % locals()
    
    log.debug(cmd)
    conn.execute(cmd)
    
    cmd = """
    CREATE INDEX taxon_id_index ON taxonomy(tax_id)
    """ 
    log.debug(cmd)
    try:
        conn.execute(cmd)
    except conn.OperationalError, msg:
        log.debug(msg)
    
    result = conn.fetchone('select * from taxonomy where tax_id=%s'%tax_id)
    
    if result:
        log.info( 'found %s' % tax_id)
        return dict([(k,result[k]) for k in tax_keys if result[k]]) 
    else:
        orig_id = tax_id
        log.info( '    constructing taxonomy for %s' % tax_id)
        
        node_data = get_node(conn, tax_id)
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
            parentdict = get_taxonomy(conn, parent_id)            
                        
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
                
        conn.execute(cmd, tax_data)
        taxonomy = taxdict
    
    return taxonomy


def get_tax_id(conn, searchstr):
    """Return taxon ID from table names"""
    
    cmd = """
    select * from names where tax_name = '%s'""" % searchstr
    node = conn.fetchone(cmd)
    if node:
        return node['tax_id']
    else:
        return None
        
def print_taxonomy(taxonomy, row_keys):
    print '\t'.join(row_keys)
    for node in taxonomy:
        print '\t'.join(['%s'%node[k] for k in row_keys])

def add_all_tax_ids(conn, tablename):
    """
    Adds taxon ids to tax_id field of target table based on 
    genus and species name.
    """
    
    cmd = """
    select genus, species, organism from %(tablename)s 
    where genus not in ('unknown')
    and species not in ('unknown') 
    group by genus, species
    """ % locals()
    all_records = conn.get_dicts(cmd)
    
    log.info("adding tax_id to %s records" % len(all_records))
    
    for row in all_records:
        print '%(organism)s' % row,
        
        genus, species = row['genus'], row['species']
        
        print 'getting tax_id ...',
        if species == 'species':
            searchterm = '%(genus)s' % row
        else:
            searchterm = '%(genus)s %(species)s' % row
        
        tax_id = get_tax_id(conn, searchterm)
        print tax_id,
        
        if tax_id:
            cmd = """
            update %(tablename)s
            set 
            tax_id = %(tax_id)s
            where genus = '%(genus)s' and species = '%(species)s'
            """ % locals()
            
#           if species == 'species':
#               print cmd
#               raw_input()
            
            try:
                conn.execute(cmd)
            except conn.error:
                print cmd
                traceback.print_exc(file=sys.stdout)
                exit()            
        print ''

def add_tax_ids_to_outliers(conn, tablename):
    """
    Adds taxon ids to tax_id field of target table for those named to
    level of family, order, etc.
    """ 

    tax_set = set('family class subphylum'.split())
    
    cmd = """
    select organism from %(tablename)s
    where tax_id is NULL
    group by organism """ % locals()
    
    all_records = conn.get_dicts(cmd)
    
    log.info("adding tax_id to %s records" % len(all_records))  
    
    for row in  all_records:
    
        organism_words = row['organism'].lower().split()
        
        if len(organism_words) == 1:
            organism_words = row['organism'].lower().split('_')
        
        try:
            tax_level, searchterm = organism_words[-2:]
        except ValueError:
            continue
        
        if tax_level not in tax_set:
            continue
                
        print 'getting tax_id for %s %s...' % (tax_level, searchterm),
        tax_id = get_tax_id(conn, searchterm)
        print tax_id,   
                
        if tax_id:
#           cmd = """
#           select organism from %(tablename)s
#           where organism regexp '%(tax_level)s %(searchterm)s'
#           group by organism
#           """ % locals()
#           
#           orgs = [d['organism'] for d in conn.get_dicts(cmd)]
#           print orgs
            
            
            cmd = """
            update %(tablename)s
            set tax_id = %(tax_id)s
            where organism regexp '%(tax_level)s[ _]+%(searchterm)s'
            """ % locals()

            conn.execute(cmd)
        
        print ''
        
        # assign a few more tax_ids for some common names
        assign_tax_id(conn, tablename, 'Ascomycete', 4890)
        assign_tax_id(conn, tablename, 'Burkholderia cepacia complex', 87882)
        assign_tax_id(conn, tablename, 'Trichophyton rubrum complex', 5550)
        

def assign_tax_id(conn, tablename, organism, tax_id):
    
    cmd = """
    update %(tablename)s
    set tax_id = %(tax_id)s
    where organism = '%(organism)s'
    """ % locals()
    
    conn.execute(cmd)


def add_all_taxonomies(conn, tablename):
    """
    Add all taxonomies for each tax_id in table "tablename"
    """

    cmd = """
    select tax_id from %(tablename)s 
    group by tax_id
    """ % locals()
    all_tax_ids = [int(x[0]) for x in conn.get_tups(cmd) if x[0]]
    all_tax_ids.sort()
    log.info("adding tax_id to %s records" % len(all_tax_ids))
    
    for tax_id in all_tax_ids:
        get_taxonomy(conn, tax_id)