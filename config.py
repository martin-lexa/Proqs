""" UniProt Columns - Columns to be request in UniProt tab-format
# https://www.uniprot.org/help/uniprotkb_column_names for available columns """
columns = 'id,entry name,length,organism,organism-id,protein names,database(PDB),database(HGNC)'

""" SwissProt Information - Which SwissProt Information is added to the Output-File
Available choices are (for an up-to-date list see: https://biopython.org/docs/dev/api/Bio.SwissProt.html): 
accessions, annotation_update, comments, created, cross_references, data_class, description, entry_name features, 
gene_name, host_organism, host_taxonomy_id, keywords, molecule_type, organelle, organism, organism_classification, 
protein_existence, references, seqinfo, sequence, sequence_length, sequence_update taxonomy_id """
swiss_prot_info = ['entry_name', 'sequence_length', 'gene_name', 'description', 'organism',
                   'seqinfo', 'sequence', 'comments', 'keywords']


