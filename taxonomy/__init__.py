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

# class Taxonomy:
# 
#     def __init__(self):
        