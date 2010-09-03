#!/usr/bin/env python

import sys
import os
import unittest
import logging
import itertools
import sqlite3 as sqlite
import shutil
import time
import pprint

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
        expect = {'class': 'synonym', 'unique': '', 'tax_name': 'all', 'tax_id': '1'}

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


    def testReadTaxonomy(self):

        names_data, nodes_data = taxonomy.read_taxonomy(self.namesfile, self.nodesfile)
        self.assertEqual(
            {'class': 'scientific name', 'unique': '', 'tax_name': 'root', 'tax_id': '1'},
            names_data.next())

        self.assertEqual(set(d['division_id'] for d in nodes_data), set(map(str, range(12))))

    def testReadBacterialTaxonomy(self):

        names_data, nodes_data = taxonomy.read_bacterial_taxonomy(self.namesfile, self.nodesfile)

        self.assertEqual(
            {'class': 'scientific name', 'unique': '', 'tax_name': 'root', 'tax_id': '1'},
            names_data.next())

        self.assertEqual(
            {'division_id': '8', 'parent_id': '1', 'embl_code': '', 'rank': 'no_rank', 'tax_id': '1'},
            nodes_data.next())

        self.assertEqual(set(d['division_id'] for d in nodes_data), set(['0','1','4','8']))


    def testCreateTaxonomyDb01(self):

        outfiles = taxonomy.get_ncbi_tax_data(dest_dir=outputdir)
        names_data, nodes_data = taxonomy.read_bacterial_taxonomy(**outfiles)

        dbname = taxonomy.create_taxonomy_db(
            names_data=itertools.islice(names_data, 0, 1000),
            nodes_data=itertools.islice(nodes_data, 0, 1000),
            dbname=self.funcname+'.db',
            dest_dir=outputdir
            )

        self.assertTrue(os.access(dbname, os.F_OK))

        con = sqlite.connect(dbname)
        synonyms = con.cursor().execute('select count(*) from names where is_primary = 0').fetchone()[0]
        self.assertEqual(synonyms, 0)

        ranks = con.cursor().execute('select rank from nodes group by rank').fetchall()
        ## rank names should not contain whitespace
        self.assertEqual(ranks, [('_'.join(x[0].split()),) for x in ranks])

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

        ranks = con.cursor().execute('select rank from nodes group by rank').fetchall()
        ## rank names should not contain whitespace
        self.assertEqual(ranks, [('_'.join(x[0].split()),) for x in ranks])


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

        # nodes.source should be zero by default
        sources = con.cursor().execute('select source_id from nodes').fetchall()
        self.assertEqual( set(x[0] for x in sources), set([1]) )

class Test00CreateFullDatabase(unittest.TestCase):

    def test1(self):

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

class TestCreateTable(unittest.TestCase):

    def setUp(self):
        self.funcname = '_'.join(self.id().split('.')[-2:])
        self.dbname = os.path.join(outputdir, self.funcname+'.db')
        try:
            os.remove(self.dbname)
        except OSError:
            pass
        self.con = sqlite.connect(self.dbname)

    def tearDown(self):
        self.con.close()

    def testCreateRanks01(self):
        taxonomy.make_ranks_db(self.con, ranks=taxonomy.tax_keys)

class TestTaxonomyClass(unittest.TestCase):

    taxid1660 = {'class': '1760',
                 'family': '2049',
                 'genus': '1654',
                 'no_rank': '131567',
                 'order': '2037',
                 'parent_id': '1654',
                 'phylum': '201174',
                 'species': '1660',
                 'subclass': '85003',
                 'suborder': '85005',
                 'superkingdom': '2',
                 'tax_id': '1660'}

    def setUp(self):
        self.funcname = '_'.join(self.id().split('.')[-2:])
        self.assertTrue(os.access(complete_test_db, os.F_OK))

        # confirm that backup database does not have taxonomy table
        con = sqlite.connect(complete_test_db)
        self.assertTrue( bool(con.cursor().execute('pragma table_info(nodes)').fetchall()) )
        self.assertTrue( bool(con.cursor().execute('pragma table_info(names)').fetchall()) )
        self.assertFalse( bool(con.cursor().execute('pragma table_info(taxonomy)').fetchall()) )
        self.dbname = os.path.join(outputdir, self.funcname+'.db')

    def test10(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)
        names_cols = tax.column_names(table_name='names')
        self.assertEqual(names_cols, ['tax_id', 'tax_name', 'is_primary'])

        nodes_cols = tax.column_names(table_name='nodes')
        self.assertEqual(nodes_cols, ['tax_id', 'parent_id', 'rank', 'embl_code', 'division_id','source_id'])

    def test20(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)
        node = tax._get_node('1660')

        self.assertEqual(node,
        {'description': None,
         'division_id': '0',
         'embl_code': 'AO',
         'parent_id': '1654',
         'rank': 'species',
         'source_id': 1,
         'source_name': 'NCBI',
         'tax_id': '1660',
         'tax_name': 'Actinomyces odontolyticus'})

    def test21(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)
        self.assertTrue(tax.has_node('1660'))
        self.assertFalse(tax.has_node('1660_a'))

    def test30(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)
        self.assertTrue( isinstance(tax, taxonomy.Taxonomy) )

    def test35(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)

        start = time.time()
        lineage = tax._get_lineage('1660')
        end1 = time.time()-start
        log.debug(pprint.pformat(lineage))
        log.info('first request %s secs' % end1)
        self.assertEqual(lineage, self.taxid1660)

        start = time.time()
        lineage = tax._get_lineage('1660')
        end2 = time.time()-start
        log.info('second request %s secs' % end2)
        log.info('speedup = %s' % (end1/end2))
        self.assertEqual(lineage, self.taxid1660)


    def test40(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)
        lineage = tax._get_lineage(1660)
        self.assertEqual(lineage, self.taxid1660)
        lineage = tax._get_lineage(1660)
        self.assertEqual(lineage, self.taxid1660)

    def test50(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)
        lineage = tax.lineage('1660')
        log.info('\n'+str(lineage))
        log.info([lineage])
        self.assertEqual(lineage.tax_id, '1660')

    def test55(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)

        self.assertRaises(ValueError,
                          tax.lineage,
                          tax_id='1660', tax_name='Actinomyces odontolyticus')

        self.assertRaises(ValueError,
                          tax.lineage)

        lineage1 = tax.lineage(tax_id='1660')
        log.info('\n'+str(lineage1))

        self.assertRaises(ValueError, tax.lineage,
                          tax_name='Actinomyces weirdii')

        lineage2 = tax.lineage(tax_name='Actinomyces odontolyticus')
        log.info('\n'+str(lineage2))

        self.assertTrue(lineage1 == lineage2)


    def test60(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)

        new_id = '1660_1'
        tax.add_node(tax_id=new_id, tax_name='Actino, Jr.', parent_id='1660', source_name='FAKE')

        lineage = tax.lineage(new_id)
        log.info(lineage)
        self.assertEqual(lineage.tax_id, new_id)

        tax.add_node(tax_id=new_id, tax_name='Actino, Jr.', parent_id='1660', source_name='FAKE')
        tax.add_node(tax_id=new_id, tax_name='Actino, III', parent_id='1660', source_name='ALSOFAKE')

    def test70(self):
        shutil.copyfile(complete_test_db, self.dbname)
        tax = taxonomy.Taxonomy(dbname=self.dbname)
        parent_id = '186802'

        new_id = '186802_1'
        tax.add_node(tax_id=new_id, tax_name='Child of Clostridiales',
        parent_id=parent_id, rank='species', source_name='FAKE')

        lineage = tax.lineage(new_id)
        log.info('\n'+str(lineage))

