#!/usr/bin/env python

def main():
    """
    Routines for building and modifying taxonomy tables in mdx database
    """

    logging.basicConfig(level=logging.INFO,
        format='%(lineno)s %(levelname)s %(message)s',
        stream=sys.stdout)

    row_keys = nodes_keys+['name']
    data_dir = '.'
    
    if not (os.access('names.dmp', os.F_OK) \
        and os.access('nodes.dmp', os.F_OK)):
        get_ncbi_tax_data(data_dir)
        
    conn = db_tools.Sqlite('ncbi_taxonomy.db', row_factory=db_tools.dict_factory, new=False)
    
    ### build the names table from NCBI data if it doesn't exist      
    if not db_tools.table_exists(conn, 'names'):    
        log.warning( 'populating names' )
        all_names_data = read_dmp(data_dir, 'names.dmp', lambda i: True)
        make_names_db(all_names_data, conn)
        log.warning( 'done populating names' )
    
    if not db_tools.table_exists(conn, 'nodes'):    
        log.warning( 'populating nodes' )
        nodes_data = read_dmp(data_dir, 'nodes.dmp')
        make_nodes_db(nodes_data, nodes_keys, conn)
        log.warning( 'done populating nodes' )

    log.warning('Creating table taxonomy')
    print get_taxonomy(conn, '287')

        
if __name__ == '__main__':
    main()