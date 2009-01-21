#!/usr/bin/env python

import sys
import os
import unittest
import logging
import itertools
import sqlite3 as sqlite
import shutil

import config
import taxonomy

log = logging

module_name = os.path.split(sys.argv[0])[1].rstrip('.py')
outputdir = config.outputdir
datadir = config.datadir 

complete_test_db = os.path.join(outputdir, 'ncbi_taxonomy.db.bak')

class TestCreateDatabase(unittest.TestCase):
    
    namesfile = os.path.join(outputdir,'names.dmp')
    nodesfile = os.path.join(outputdir,'nodes.dmp')    

    def setUp(self):
        self.funcname = '_'.join(self.id().split('.')[-2:])
    
    def testGetNCBIData(self):
        outfiles = taxonomy.get_ncbi_tax_data(dest_dir=outputdir)
        
        for key, fname in outfiles.items():
            log.info('checking %s' % fname)
            self.assertTrue(os.access(fname, os.F_OK))
        
    def testReadDmp01(self):
        
        data = taxonomy.read_dmp(
            infile=self.namesfile, 
            keys=taxonomy.names_keys, 
            condition=None)
        
        firstline = data.next()
        expect = {'class': 'synonym', 'unique': '', 'name': 'all', 'tax_id': '1'}
        
        log.info('firstline: %s' % `firstline`)
        log.info('expect: %s' % `expect`)
        
        self.assertEqual(expect, firstline)

    def testReadDmp02(self):
        
        data = taxonomy.read_dmp(
            infile=self.nodesfile, 
            keys=taxonomy.nodes_keys, 
            condition=None)

        firstline = data.next()
        expect = {'division_id': '8', 'parent_id': '1', 'embl_code': '', 'rank': 'no rank', 'tax_id': '1'}
        
        log.info('firstline: %s' % `firstline`)
        log.info('expect: %s' % `expect`)
        
        self.assertEqual(expect, firstline)
        
    def testReadBacterialTaxonomy(self):
        
        names_data, nodes_data = taxonomy.read_bacterial_taxonomy(self.namesfile, self.nodesfile)
                                        
        self.assertEqual(
            {'class': 'scientific name', 'unique': '', 'name': 'root', 'tax_id': '1'}, 
            names_data.next())

        self.assertEqual(
            {'division_id': '8', 'parent_id': '1', 'embl_code': '', 'rank': 'no rank', 'tax_id': '1'},
            nodes_data.next())       

    def testCreateBacterialTaxonomyDb01(self):

        outfiles = taxonomy.get_ncbi_tax_data(dest_dir=outputdir)
        names_data, nodes_data = taxonomy.read_bacterial_taxonomy(**outfiles)
    
        dbname = taxonomy.create_bacterial_taxonomy_db(
            names_data=itertools.islice(names_data, 0, 1000),
            nodes_data=itertools.islice(nodes_data, 0, 1000),
            dbname=self.funcname+'.db',
            dest_dir=outputdir
            )
        
        self.assertTrue(os.access(dbname, os.F_OK))
        
        con = sqlite.connect(dbname)
        synonyms = con.cursor().execute('select count(*) from names where is_primary = 0').fetchone()[0]
        self.assertEqual(synonyms, 0)
        
    def testCreateBacterialTaxonomyDb02(self):

        outfiles = taxonomy.get_ncbi_tax_data(dest_dir=outputdir)
        names_data, nodes_data = taxonomy.read_bacterial_taxonomy(primary_only=False, **outfiles)
    
        dbname = taxonomy.create_bacterial_taxonomy_db(
            names_data=itertools.islice(names_data, 0, 1000),
            nodes_data=itertools.islice(nodes_data, 0, 1000),
            dbname=self.funcname+'.db',            
            dest_dir=outputdir
            )
            
        self.assertTrue(os.access(dbname, os.F_OK))
        
        con = sqlite.connect(dbname)
        synonyms = con.cursor().execute('select count(*) from names where is_primary = 0').fetchone()[0]        
        self.assertEqual(synonyms, 772)
        
    def testCreateBacterialTaxonomyDb03(self):

        outfiles = taxonomy.get_ncbi_tax_data(dest_dir=outputdir)
        names_data, nodes_data = taxonomy.read_bacterial_taxonomy(primary_only=False, **outfiles)
        
        dbname = complete_test_db
        
        if not os.access(dbname, os.F_OK):        
            log.warning('creating %s' % dbname)
            dbname = taxonomy.create_bacterial_taxonomy_db(
                names_data=names_data,
                nodes_data=nodes_data,
                dbname=dbname,
                dest_dir=outputdir
                )
            self.assertTrue(os.access(dbname, os.F_OK))
        else:
            log.info('%s exists, skipping this test' % dbname)
            
class TestTaxonomyClass(unittest.TestCase):
    
    def setUp(self):
        self.funcname = '_'.join(self.id().split('.')[-2:])
        self.assertTrue(os.access(complete_test_db, os.F_OK))
        self.dbname = os.path.join(outputdir, self.funcname+'.db')
        
    def test1(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)
        names_cols = tax.column_names(table_name='names')
        self.assertEqual(names_cols, ['tax_id', 'tax_name', 'is_primary'])
        
        nodes_cols = tax.column_names(table_name='nodes')
        self.assertEqual(nodes_cols, ['tax_id', 'parent_id', 'rank', 'embl_code', 'division_id'])        
