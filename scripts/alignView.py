#!/usr/local/bin/python

import sys
import os
import pprint
import traceback
import time
import string
import logging
from optparse import OptionParser

import Seq
import Menu

from blast2tree import util, parsing, config

__version__ = "$Id$"

log = logging.getLogger('')
util.setup_logging(config.console_level)

path = os.path.abspath('.')

def show_more_options(menu):
    menu.visible = menu.extended_view

def show_fewer_options(menu):
    menu.visible = menu.main_view

def guess_file_format(infile):
    
    firstline = open(infile).readline().strip()
    
    if infile.endswith('.fasta') or firstline.startswith('>'):
        return 'fasta'
    elif infile.endswith('.aln'):
        return 'aln'
    else:
        print 'The format of the input file cannot be determined; please specify a format'
        return Menu.offer_list([('aln','Clustal .aln alignment format'),('fasta','fasta format')], cls=False)
    
    
def main():

    usage = "%prog [options] input.fasta\n"
    usage += 'View an aligned set of sequences in fasta format.'
    
    parser = OptionParser(usage=usage, version=__version__)

    parser.add_option("-f", "--infile", dest="infile",
        help="input FILE containing sequence alignment", 
        metavar="FILE", default='')

    parser.add_option("-o", "--outfile", dest="outfile",
        help="write output to a pdf file in the same directory as the input file", 
        metavar="NAME", default='')

    parser.add_option("-e", "--show-settings", dest="show_settings",
        help="show settings", 
        action='store_true', default=False)     
        
    parser.add_option("-s", "--no_menu", dest="no_menu",
        help="suppress the interactive menu at startup", 
        action='store_true', default=False)         

    parser.add_option("-c", "--no_consensus", dest="no_consensus",
        help="do not show a consensus sequence", 
        action='store_true', default=False) 

    parser.add_option("-d", "--diff", dest="diff",
        help="if the value is 'consensus' display positions identical to the corresponding position in the consensus as a '.', or provide the name of a sequence in the alignment for comparison. Provide None to suppress character replacement.", default='consensus')    

    parser.add_option("-N", "--number_by", dest="number_by",
        help="number the aligned positins according to the indicated sequence. This option is useful for generating an alignment numbered according to a reference strain, for example.", default='consensus')

    parser.add_option("-x", "--exclude_invariant", dest="exclude_invariant",
        help="only show columns with at least min_subs non-consensus bases (set min_subs using the -i option)", 
        action='store_true', default=False) 

    parser.add_option("-i", "--min_subs", dest="min_subs",
        help="minimum NUMBER of substitutions required to define a position as variable", 
        metavar="NUMBER", default=1, type='int')    

    parser.add_option("-n", "--max_name_width", dest="max_name_width",
        help="maximum width of sequence name", 
        metavar="NUMBER", default=35, type='int')   

    parser.add_option("-w", "--seq_width", dest="seq_width",
        help="width of sequence to display in each block", 
        metavar="NUMBER", default=115, type='int')

    parser.add_option("-F", "--fontsize", dest="fontsize",
        help="Font size for pdf output", 
        metavar="NUMBER", default=7, type='int')

    parser.add_option("-U", "--uppercase", dest="upper",
        help="Convert all characters to upper case", 
        action='store_true', default=False)

    parser.add_option("-C", "--case", dest="case",
        help="Convert all characters to a uniform case ('upper','lower')", 
        metavar='CASE', default=None, choices=['upper','lower'])

    parser.add_option("-p", "--seqs_per_page", dest="seqs_per_page",
        help="Sequences (lines) per page of pdf output", 
        metavar="NUMBER", default=75, type='int')

    parser.add_option("-O", "--orientation", dest="orientation",
        help="Choose from portrait or landscape", 
        metavar="ORIENTATION", default='portrait')

    parser.add_option("-q", "--quiet", dest="quiet",
        help="suppress screen output", 
        action='store_true', default=False)
    
    (options, args) = parser.parse_args()

    if options.no_menu and options.infile:
        optdict = dict(
        [(opt.dest, getattr(options, opt.dest)) for opt in parser.option_list if opt.dest])
                
        if optdict['show_settings']:
            pprint.pprint(optdict)
            sys.exit()
        
    #### set up interactive menu        
    else:
        menu = Menu.Menu()
        menu.xlabel = 'Format alignment and exit'
        
        ################ define option sets
                        
        # add options to the menu as specified in the OptParse parser object
        menu.add_parser_data(parser, options)

        menu.add_option(key='show_more_options', 
        label='Show more menu options', val='', 
        handler=show_more_options)  

        menu.add_option(key='show_fewer_options', 
        label='Show fewer menu options', val='', 
        handler=show_fewer_options) 

        # menu initially shows only top-level commands
        main_view = set("""infile outfile show_more_options""".split())
        
        extended_view = set("""infile outfile show_fewer_options show_settings
        name_width seq_width no_consensus diff exclude_invariant 
        min_subs seqs_per_page fontsize orientation""".split())     

        menu.visible = main_view
        
        menu.main_view = main_view
        menu.extended_view = extended_view
        
        ####### begin interactive session
        while True:
            optdict = menu.run()
            if not optdict['infile']:
                raw_input( 
                'No input file was specified (press return to continue) ')
            # check for stdin
            else:
                break
            
        if optdict['show_settings']:
            pprint.pprint(optdict)
            raw_input('Press return to continue ')  
                
    ######### end interactive part
    inpath, in_name = os.path.split(optdict['infile'])
    infile = os.path.join(inpath, in_name)
    inpath = os.path.abspath(inpath)
    
    
    ### 
    seq_width = optdict['seq_width']
    max_name_width = optdict['max_name_width']
    include_consensus = not optdict['no_consensus']
    diff = optdict['diff']
    exclude_invariant = optdict['exclude_invariant']
    min_subs = optdict['min_subs']
    quiet = optdict['quiet']
    fontsize = optdict['fontsize']
    seqs_per_page = optdict['seqs_per_page']
    orientation = optdict['orientation']
    number_by = optdict['number_by']
    case = optdict['case']
    
    screen = sys.stdout
    
    instr = open(infile).read()
    file_format = guess_file_format(infile)

    try:
        if file_format == 'fasta':
            seqlist = Seq.io_fasta.read(instr)
        elif file_format == 'aln':
            seqlist = Seq.io_clustal.readAlnStr(instr)
    except Seq.io_fasta.FormatError:
        print 'There was an error in the alignment format of this file. Please ensure that the file is actually in "%s" format and try again.' % file_format
        raw_input('Press return to exit ')
        sys.exit()

    pages = Seq.sequtil.reformat_alignment(
        seqlist, 
        max_name_width, 
        seq_width, 
        include_consensus, 
        diff, 
        exclude_invariant, 
        min_subs, 
        seqs_per_page,
        '.',
        number_by,
        case)

    if not quiet:
        for page in pages:          
            screen.write('\n'.join(page) + '\n')
            screen.write('#\n')
    
    if optdict['outfile']:
        pdf_name = os.path.splitext(optdict['outfile'])[0] + '.pdf'             
        print 'writing output to %s' % pdf_name     
        parsing.write_pdf(pages, pdf_name, fontsize, orientation)
        
    if os.name != 'posix' and not options.no_menu:
        raw_input('press return to exit ')

if __name__ == '__main__':
    try:
        main()
    except (SystemExit,KeyboardInterrupt):
        sys.exit('\nQuitting\n')    
    except:
        traceback.print_exc(file=sys.stdout)
        raw_input('press return to exit ')
    
