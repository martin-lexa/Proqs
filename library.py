import requests
import pandas as pd
from io import StringIO
from Bio import ExPASy, SwissProt
from requests import Response
import config
import datetime
from contextlib import redirect_stdout
import logging


# pandas table options (for the command line output, without this rows/columns get cut)
DESIRED_WIDTH = 1080
pd.set_option('display.width', DESIRED_WIDTH)
pd.set_option('display.max_columns', None)


def handle_request(args):
    """Starting point for requests
    checks the given arguments and calls the appropriate functions to handle the request"""
    func_map = {"swissprot": swissprot_request, "pdb": pdb_request}

    if args.dsv_list:
        args.request = convert_dsv_file(args.request, args.delim)

    for uniprot_id in args.request:
        service = args.service
        entry_id = uniprot_id
        if 'uniref' in args.service:
            service = 'uniref'
            if 'uniref' == args.service:
                args.service = 'uniref100'
            entry_id = f"{args.service}_{uniprot_id}"
        elif 'uniparc' == args.service:
            entry_id = convert_uniprot_id('UPARC', uniprot_id)

        response = uni_all_request(service, query=entry_id,
                                   format=args.format,
                                   columns=config.columns,
                                   limit='50')

        save_response_to_file(response, args.service, entry_id, args.format)

        for adb in args.additional_databases:
            func_map[adb](uniprot_id)


def save_response_to_file(response, database, entry_id, format):
    with open(f"{database}_{entry_id}_{datetime.datetime.now().strftime('%Y-%m-%d_%X')}.{format}", mode='wb') as f_out:
        f_out.write(response.content)


def convert_dsv_file(dsv_file, sep):
    """Takes a delimiter-separated value file that is a list of IDs and iterates over the IDs"""
    with open(dsv_file[0]) as f_in:
        list = f_in.read()
        return list.split(sep)


def convert_uniprot_id(database, uniprot_id):
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


def server_request(base_url, **kwargs) -> object:
    """General server request
    Takes a request and returns a single entry"""
    params = ''
    response: Response = requests.get(f'{base_url}{params}', params=kwargs)
    print(f"Requested URL: {response.url}")
    if not response.ok:
        response.raise_for_status()
    return response


def uni_all_request(service, **kwargs):
    """Uniprot server request
    takes the specific service (uniprot, uniref, uniproc) and any additional arguments
    calls server_request() and returns the single entry returned"""
    response = server_request(f'http://www.uniprot.org/{service}/', **kwargs)
    # these lines are for visual feedback in the terminal during coding and testing,
    # but they don't work with all available formats
    # uniprot_list = pd.read_table(StringIO(response.text))
    # uniprot_list.rename(columns={'Organism ID': 'ID'}, inplace=True)
    # print(uniprot_list)
    return response


def swissprot_request(uniprot_id):
    handle = ExPASy.get_sprot_raw(uniprot_id)
    try:
        sp_rec = SwissProt.read(handle)
    except ValueError:
        logging.warning(f"WARNING: Accession {accession} not found")
    with open(f"SwissProt_{uniprot_id}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
              mode='a') as f_out:
        for info in config.swiss_prot_info:
            with redirect_stdout(f_out):
                print(info, end=": ")
                exec("print(sp_rec." + info + ")")


def pdb_request(uniprot_id):
    pdb_ids_table = convert_uniprot_id('PDB_ID', uniprot_id)
    converted_list = pd.read_table(StringIO(pdb_ids_table.text))
    with open(f"PDB_{uniprot_id}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
              mode='a') as f_out:
        for entry in converted_list['To']:
            response: Response = requests.get(f'https://data.rcsb.org/rest/v1/core/entry/{entry}')
            if not response.ok:
                response.raise_for_status()
            f_out.write(f"PDB-ID: {entry}\n{response.text}")


if __name__ == '__main__':

    pass
