import requests
import pandas as pd
from io import StringIO
from Bio import ExPASy, SwissProt
from requests import Response
import config
import datetime
from contextlib import redirect_stdout


# pandas table options (for the command line output, without this rows/columns get cut)
desired_width = 1080
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', None)


# def request_chosen_services
# iterates over chosen services and call service requests


def handle_request(args):
    """Starting point for requests
    checks the given arguments and calls the appropriate functions to handle the request"""
    if args.dsv_list:
        args.request = convert_dsv_list(args.request, args.delim)

    if 'tab' == args.format:
        for uniprot_id in args.request:
            response = uniprot_request(args.service, query=uniprot_id,
                                       format='tab',
                                       columns=config.columns,
                                       limit='50')
            # do something with the return value (like maybe save the fucking file)
            save_response_to_file(response, 'UniProt', uniprot_id, args.format)

    else:
        for uniprot_id in args.request:
            response = requests.get('http://www.uniprot.org/uniprot/' + uniprot_id + '.' + args.format)
            save_response_to_file(response, 'UniProt', uniprot_id, args.format)

    if 'swissprot' in args.additional_databases:
        handle = ExPASy.get_sprot_raw(uniprot_id)
        try:
            sp_rec = SwissProt.read(handle)
        except ValueError:
            print("WARNING: Accession %s not found" % accession)
        with open("SwissProt_" + uniprot_id + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%X").replace(":", "-"),
                  mode='a') as f_out:
            for info in config.swiss_prot_info:
                with redirect_stdout(f_out):
                    exec("print(sp_rec." + info + ")")


def save_response_to_file(response, database, entry_id, format):
    with open(database + "_" + entry_id + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%X").replace(":", "-")
              + "." + format,
              mode='wb') as f_out:
        f_out.write(response.content)

def convert_dsv_list(id_list, sep=","):
    """Takes a delimiter-separated value file that is a list of IDs and iterates over the IDs"""
    with open(id_list[0]) as f_in:
        list = f_in.read()
        converted_list = list.split(sep)
        return converted_list


def convert_uniprot_id(database='PDB_ID', uniprot_id='P62979'):
    """Takes a database and an UniprotID and returns the corresponding ID in the given database"""
    params = {
        'from': 'ACC+ID',
        'to': database,
        'format': 'tab',
        'query': uniprot_id
    }
    response: Response = requests.get('https://www.uniprot.org/uploadlists', params=params)
    if not response.ok:
        response.raise_for_status()
    return response


def server_request(base_url, entry_id, **kwargs) -> object:
    """General server request
    Takes a request and returns a single entry"""
    params = ''
    response: Response = requests.get(f'{base_url}{entry_id}{params}', params=kwargs)
    print(response.url)
    if not response.ok:
        response.raise_for_status()
    return response


def uniprot_request(service, **kwargs):
    """Uniprot server request
    takes the specific service (uniprot, uniref, uniproc, taxonomy) and any additional arguments
    calls server_request() and returns the single entry returned"""
    response = server_request('http://www.uniprot.org/' + service + '/', entry_id='', **kwargs)
    uniprot_list = pd.read_table(StringIO(response.text))
    uniprot_list.rename(columns={'Organism ID': 'ID'}, inplace=True)
    print(uniprot_list)

    return response


if __name__ == '__main__':

    # SwissProt
    handle = ExPASy.get_sprot_raw('P62979')
    sp_rec = SwissProt.read(handle)

    print(sp_rec.entry_name, sp_rec.sequence_length, sp_rec.gene_name)
    print(sp_rec.description)
    print(sp_rec.organism, sp_rec.seqinfo)
    print(sp_rec.sequence)
    print(sp_rec.comments)
    print(sp_rec.keywords)

    from collections import defaultdict

    done_features = set()
    print(len(sp_rec.features))
    for feature in sp_rec.features:
        if feature in done_features:
            continue
        else:
            done_features.add(feature)
            print(feature)
    print(len(sp_rec.cross_references))
    per_source = defaultdict(list)
    for xref in sp_rec.cross_references:
        source = xref[0]
        per_source[source].append(xref[1:])
    print(per_source.keys())
    done_GOs = set()
    print(len(per_source['GO']))
    for annot in per_source['GO']:
        if annot[1][0] in done_GOs:
            continue
        else:
            done_GOs.add(annot[1][0])
    print(annot)

    # multiple SwissProt Records
    accessions = ["O23729", "O23730", "O23731"]
    records = []

    for accession in accessions:
        handle = ExPASy.get_sprot_raw(accession)
        record = SwissProt.read(handle)
        records.append(record)
