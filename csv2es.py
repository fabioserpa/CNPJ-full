import sys

import argparse
import csv
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk, bulk


def prepare_company_docs(es, index, id, filename, delimiter=','):
  """
    Use generator to iterate through all the lines in CSV files
  """
  def generate():
    with open(filename, 'r') as doc_file:
      print("Pushing {} into ElasticSearch".format(filename))
      header_reader = csv.reader(doc_file)
      fieldnames = next(header_reader, None)
      reader = csv.DictReader(doc_file, delimiter=delimiter, fieldnames=fieldnames)
      for row in reader:
        yield {
            "_index": index,
            "_type": "document",
            "_op_type": "index",
            "_id": row[id],
            "_source": row
        }

  return generate

# def prepare_partners_docs(es, index, filename, delimiter=','):
#   def generate():
#     with open(filename, 'r') as doc_file:
#       print("Pushing {} into ElasticSearch".format(filename))
#       header_reader = csv.reader(doc_file)
#       fieldnames = next(header_reader, None)
#       reader = csv.DictReader(doc_file, delimiter=delimiter, fieldnames=fieldnames)

#       cnpj = None
#       prev_cnpj = None
#       partners = [ ]
#       for row in reader:
#         cnpj = row['cnpj']

#         if prev_cnpj == cnpj:
#           partners.append(row)
#         else:
#           yield {
#               "_index": index,
#               "_type": "document",
#               "_op_type": "update",
#               "_id": prev_cnpj,
#               "_source": { "socios": partners }
#           }
#           prev_cnpj = cnpj
#           partners = [ row ]

#       # Run for last row/set of rows
#   return generate


def publish_to_es(es, docs, docs_per_chunk):
  # bulk(es, docs())
  for success, info in parallel_bulk(es, docs(), chunk_size=docs_per_chunk):
    if not success:
      print('A document failed:', info)


def cli():
  parser = argparse.ArgumentParser(description='Parse Arguments')
  parser.add_argument('elasticsearch_url',
                    help='Elastic Search Endpoint')
  parser.add_argument('--elasticsearch_port', type=int, default=443,
                    help='Elastic Search Endpoint Port')
  parser.add_argument('--files_dir', default='csv',
                    help='Directory where empresas.csv, socios.csv and cnaes_secundarias.csv are stored')
  parser.add_argument('--docs_per_chunk', type=int, default=2000,
                    help='Number of documents uploaded in each bulk operation')
  args = parser.parse_args()

  es = Elasticsearch(
    [args.elasticsearch_url],
    port=args.elasticsearch_port,
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
  )

  companies = prepare_company_docs(es,
                index='empresas',
                id='cnpj', 
                filename='{}/{}'.format(args.files_dir,'empresas.csv')
              )
  publish_to_es(es, companies, args.docs_per_chunk)

  cnaes = prepare_docs(es,
            index='cnaes_secundarios',
            id='cnpj',
            filename='{}/{}'.format(args.files_dir, 'cnaes_secundarios.csv')
          )
  publish_to_es(es, cnaes, args.docs_per_chunk)

  # socios = prepare_partners_docs(es,
  #           index='empresas',
  #           filename='{}/{}'.format(args.files_dir, 'socios.csv')
  #         )
  # publish_to_es(es, socios, args.docs_per_chunk)

if __name__ == "__main__":
    cli()
