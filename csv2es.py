import argparse
import csv
import json
import os
from elasticsearch import Elasticsearch, Urllib3HttpConnection
from elasticsearch.helpers import parallel_bulk, bulk

class MyUrllib3HttpConnection(Urllib3HttpConnection):
    def __init__(self, *args, **kwargs):
        extra_headers = kwargs.pop('extra_headers', {})
        super(MyUrllib3HttpConnection, self).__init__(*args, **kwargs)
        self.headers.update(extra_headers)

def prepare_docs(es, index, filename, id=None, delimiter=','):
  """
    Use generator to iterate through all the lines in CSV files
  """
  def generator():
    with open(filename, 'r') as doc_file:
      print("Pushing '{}' into ElasticSearch at index '{}'".format(filename, index))
      header_reader = csv.reader(doc_file)
      fieldnames = next(header_reader, None)
      reader = csv.DictReader(doc_file, delimiter=delimiter, fieldnames=fieldnames)
      for row in reader:
        yield {
            "_index": index,
            "_type": "document",
            "_op_type": "index",
            "_id": row.get(id, None),
            "_source": row
        }

  return generator


def publish_to_es(es, docs, docs_per_chunk):
  for success, info in parallel_bulk(es, docs(), chunk_size=docs_per_chunk):
    if not success:
      print('A document failed:', info)


def cli():
  parser = argparse.ArgumentParser(description='Parse Arguments')
  parser.add_argument('index_sufix',
                    help='Sufix for the index. e.g. 2019_3')
  parser.add_argument('elasticsearch_url',
                    help='Elastic Search Endpoint')
  parser.add_argument('--elasticsearch_port', type=int, default=443,
                    help='Elastic Search Endpoint Port')
  parser.add_argument('--files_dir', default='csv',
                    help='Directory where empresas.csv, socios.csv and cnaes_secundarias.csv are stored')
  parser.add_argument('--docs_per_chunk', type=int, default=3000,
                    help='Number of documents uploaded in each bulk operation')
  args = parser.parse_args()

  if os.environ.get('API_KEY_ID', None) is None:
    raise KeyError("Environment Variable 'API_KEY_ID' not found")

  if os.environ.get('API_KEY', None) is None:
    raise KeyError("Environment Variable 'API_KEY' not found")

  print("Version {}".format(args.index_sufix))
  es = Elasticsearch(
    [args.elasticsearch_url],
    port=args.elasticsearch_port,
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    connection_class=MyUrllib3HttpConnection,
    extra_headers={
      os.environ.get('API_KEY_ID'): os.environ.get('API_KEY')
    }
  )

  index_tpl = '{name}_{version}'

  companies = prepare_docs(es,
                index=index_tpl.format(name='empresas', version=args.index_sufix),
                id='cnpj', 
                filename='{}/{}'.format(args.files_dir,'empresas.csv')
              )
  publish_to_es(es, companies, args.docs_per_chunk)

  cnaes = prepare_docs(es,
            index=index_tpl.format(name='cnaes_secundarios', version=args.index_sufix),
            id='cnpj',
            filename='{}/{}'.format(args.files_dir, 'cnaes_secundarios.csv')
          )
  publish_to_es(es, cnaes, args.docs_per_chunk)

  socios = prepare_docs(es,
            index=index_tpl.format(name='socios', version=args.index_sufix),
            filename='{}/{}'.format(args.files_dir, 'socios.csv')
          )
  publish_to_es(es, socios, args.docs_per_chunk)


if __name__ == "__main__":
    cli()
