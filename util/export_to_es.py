import json
import os
import time
from controllers import common
from util import exceptions
from util import elasticsearch_client
from util import cloudant_client
from util.time_util import timeit


MAX_GET_DOC_COUNT = 10000
MAX_POST_DATA_LEN = 1024000


class Exporter(object):
    def __init__(self, cloudant_db, es_client):
        self.cloudant_db = cloudant_db
        self.es_client = es_client

    def is_id_valid(self, local_id):
        try:
            common.validate_id(local_id)
            return True
        except exceptions.BadRequestError:
            return False

    @timeit
    def export_all(self):
        self.export_projects()
        self.export_notes()
        self.export_occurrences()

    @timeit
    def export_projects(self):
        writer = self.es_client.get_bulk_writer('grafeas', 'Project', MAX_POST_DATA_LEN)
        self._export_docs(writer, 'Project')
        writer.close()

    @timeit
    def export_notes(self):
        writer = self.es_client.get_bulk_writer('grafeas', 'Note', MAX_POST_DATA_LEN)
        self._export_docs(writer, 'Note')
        writer.close()

    @timeit
    def export_occurrences(self):
        writer = self.es_client.get_bulk_writer('grafeas', 'Occurrence', MAX_POST_DATA_LEN)
        self._export_docs(writer, 'Occurrence')
        writer.close()

    def _export_docs(self, writer, doc_type):
        skip = 0
        while True:
            start_time = time.time()
            print("Exporting next {} docs (skip={})...".format(MAX_GET_DOC_COUNT, skip))
            docs = self.cloudant_db.find(
                filter_={'doc_type': doc_type}, index="DT",
                skip=skip, limit=MAX_GET_DOC_COUNT)

            n = 0
            for doc in docs:
                if doc_type in ['Note', 'Occurrence']:
                    if not self.is_id_valid(doc['project_id']):
                        print("INVALID ID: {}".format(doc['project_id']))
                        continue

                if not self.is_id_valid(doc['id']):
                    if '/' in doc['id']:
                        doc['id'] = doc['id'].replace('/', '%252F')
                    else:
                        print("INVALID ID: {}".format(doc['id']))
                        continue

                doc_id = doc['_id']
                create_timestamp = doc.get('create_timestamp')
                if create_timestamp:
                    doc['create_timestamp'] = int(round(create_timestamp * 1000))

                update_timestamp = doc.get('update_timestamp')
                if update_timestamp:
                    doc['update_timestamp'] = int(round(update_timestamp * 1000))

                doc.pop('_id', None)
                doc.pop('_rev', None)
                doc.pop('doc_type', None)

                writer.create(doc, doc_id)
                n += 1

            writer.flush()
            end_time = time.time()
            skip += MAX_GET_DOC_COUNT
            print("{} docs exported in {} secs ({} total)".format(n, int(end_time - start_time), skip))

            if len(docs) < MAX_GET_DOC_COUNT:
                break

        print("{} TOTAL DOCS EXPORTED".format(skip))

    def query_all_notes(self):
        results = self.es_client.find(index='grafeas', doc_type='Note', filter_={'kind': 'CARD'})
        print(json.dumps(results, indent=2))


cloudant_db = cloudant_client.CloudantDatabase(
    os.environ['CLOUDANT_URL'], 'grafeas',
    os.environ['CLOUDANT_USERNAME'],
    os.environ['CLOUDANT_PASSWORD'])


es_client = elasticsearch_client.ComposeElasticsearchClient(
    os.environ['ES_URL'].split(','),
    os.environ['ES_USERNAME'],
    os.environ['ES_PASSWORD'])


if es_client.index_exists('grafeas'):
    es_client.delete_index('grafeas')
es_client.create_index('grafeas')
grafeas_index = es_client.get_index('grafeas')
print(json.dumps(grafeas_index, indent=2))

exporter = Exporter(cloudant_db, es_client)
exporter.export_all()

'''
exporter.query_all_notes()
'''
