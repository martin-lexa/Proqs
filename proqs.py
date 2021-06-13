from typing import Any

import argparse
import library
import logging

if __name__ == '__main__':
    # implement additional databases
    parser = argparse.ArgumentParser(description='Retrieve Protein Database Entries')
    parser.add_argument('request', metavar='request', nargs='+',
                        help='one or more Uniprot-ID(s) (default) or a delimiter-separated values file to be requested'
                             ' (must be specified with -l)')
    parser.add_argument('-l', '--list', dest='dsv_list', action='store_true',
                        help='specifies that the positional argument refers to a file containing a list of IDs')
    parser.add_argument('-d', '--delimiter', '--separator', dest='delim', default=',',
                        help='specifies delimiter used in the provided list of Uniprot-IDs (default: ",")')
    parser.add_argument('-f', '--format', nargs='?', default='tab',
                        choices=['html', 'tab', 'xls', 'fasta', 'gff', 'txt', 'xml', 'rdf', 'list', 'rss'],
                        help='output format for UniProt entry')
    parser.add_argument('--service', '--uniprotservice', default='uniprot',
                        choices=['uniprot', 'uniref', 'uniref100', 'uniref90', 'uniref50', 'uniparc'],
                        help='chooses uniprot service to query. "uniref" defaults to UniRef100')
    parser.add_argument('-a', '--databases', '--dbs', dest='additional_databases', nargs='*',
                        choices=['swissprot', 'pdb'],
                        help='to get results from additional databases; at the moment only SwissProt and PDB')

    args = parser.parse_args()
    logging.debug(args)

    request = library.handle_request(args)
