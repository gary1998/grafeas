'''
Created on Sep 1, 2016

@author: alberto
'''

import elasticsearch
import json
import hashlib
import logging
from urllib import parse
from io import StringIO
import threading
from util import dict_util
from util import exceptions


logger = logging.getLogger("util.elasticsearch_client")


class ElasticsearchBulkError(Exception):
    def __init__(self, total, in_error, errors):
        # The errors array can be huge, take only the first element
        super().__init__(
            "Elasticsearch bulk errors: total={}, in_error={}, first_error(if any)={}".format(
                total, in_error, errors[0] if errors else []))
        self.total = total
        self.in_error = in_error
        self.errors = errors


class ElasticsearchQueryBuilder(object):
    def __init__(self):
        self.body = {
            "query": {
                "match_all": {}
            }
        }

    def match_term(self, field_name, field_value):
        self.body['query'].pop('match_all', None)
        dict_util.merge(
            self.body,
            {
                "query": {
                    "bool": {
                        "filter": [
                            { "term": { field_name: field_value }}
                        ]
                    }
                }
            })

    def with_start_time(self, field_name, field_value):
        self.body['query'].pop('match_all', None)
        dict_util.merge(
            self.body,
            {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    field_name: {
                                        "gte": field_value,
                                        "format": "epoch_millis"
                                    }
                                }
                            }
                        ]
                    }
                }
            })

    def with_end_time(self, field_name, field_value):
        self.body['query'].pop('match_all', None)
        dict_util.merge(
            self.body,
            {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    field_name: {
                                        "lte": field_value,
                                        "format": "epoch_millis"
                                    }
                                }
                            }
                        ]
                    }
                }
            })

    def with_time_interval(self, field_name, field_value):
        dict_util.merge(
            self.body,
            {
                "aggs": {
                    "time_series": {
                        "date_histogram": {
                            "field": field_name,
                            "interval": field_value,
                            "format": "epoch_millis"
                        }
                    }
                }
            })

    def sum_by(self, *field_names):
        aggs = {}
        for f in field_names:
            aggs[f] = {
                "sum": {
                    "field": f
                }
            }

        dict_util.merge(
            self.body,
            {
                "aggs": aggs,
                "size": 0
            })

    def sort_by(self, field_name, order="asc"):
        dict_util.merge(
            self.body,
            {
                "sort": [
                    { field_name: {"order": order}}
                ]
            })

    def with_size(self, size):
        self.body['size'] = size


class ResourceType(object):
    def __init__(self, name, key_field_names):
        self.name = name
        self.key_field_names = key_field_names

    def build_id(self, resource):
        resource_sha = hashlib.sha1()
        for field_name in self.key_field_names:
            value = resource[field_name]
            resource_sha.update(value.encode('utf-8'))

        return resource_sha.hexdigest()


class ElasticsearchBulkWriter(object):
    '''
    Implements a generic Elasticsearch buffered bulk data writer.
    Insert and update operations are implemented.
    Update is implemented as an `update doc` operation, with a retry on conflict policy = 3.
    '''

    CREATE = 1
    INDEX  = 2
    UPDATE = 3
    DELETE = 4

    def __init__(self, client, index: str, resource_type: ResourceType, max_buf_len: int):
        self.client = client
        self.index = index
        self.resource_type = resource_type
        self.buf = StringIO()
        self.max_buf_len = max_buf_len
        self.lock = threading.Lock()

    def create(self, doc):
        self._write(doc, ElasticsearchBulkWriter.CREATE)

    def create_or_update(self, doc):
        self._write(doc, ElasticsearchBulkWriter.INDEX)

    def update(self, doc):
        self._write(doc, ElasticsearchBulkWriter.UPDATE)

    def delete(self, key_fields):
        self._write(key_fields, ElasticsearchBulkWriter.DELETE)

    def _write(self, doc, action):
        with self.lock:
            if self.buf.tell() > self.max_buf_len:
                self.flush()

            doc_id = self.resource_type.build_id(doc)
            if action == ElasticsearchBulkWriter.CREATE:
                option = {
                    'create': {
                        '_id': doc_id
                    }
                }
                data = doc
            elif action == ElasticsearchBulkWriter.INDEX:
                option = {
                    'index': {
                        '_id': doc_id
                    }
                }
                data = doc
            elif action == ElasticsearchBulkWriter.UPDATE:
                option = {
                    'update': {
                        '_id': doc_id,
                        '_retry_on_conflict': 3
                    }
                }
                data = {"doc": doc}
            else:
                option = {
                    'delete': {
                        '_id': doc_id
                   }
                }

            json.dump(option, self.buf)
            self.buf.write('\n')
            if action != ElasticsearchBulkWriter.DELETE:
                json.dump(data, self.buf)
            self.buf.write('\n')

    def flush(self):
        # Index/update the last docs in the buffer
        with self.lock:
            if self.buf.tell() > 0:
                self.client._bulk(
                    self.index,
                    self.resource_type.name,
                    self.buf.getvalue())
                self.buf.close()
                self.buf = StringIO()

    def close(self):
        self.flush()
        self.buf.close()


class ElasticsearchClient(object):
    DEFAULT_SCROLL_SIZE = 1000
    DEFAULT_SEARCH_SIZE = 10000
    MAX_POST_DATA_LEN = 104857600  # 100 MB (max allowed HTTP POST content length)
    REQUEST_TIMEOUT = 60

    def __init__(self, config):
        super().__init__()
        logger.debug("Initializing elasticsearch client: %s ...",
                     ElasticsearchClient._remove_sensitive_info(config))

        es_config = {
            'send_get_body_as': 'POST',
            'sniff_on_start': False,
            'sniff_on_connection_fail': False,
            'timeout': 60,
            'retry_on_timeout': True,
            'max_retries': 10
        }

        es_config.update(config)
        hosts = es_config.pop('hosts')
        self.client = elasticsearch.Elasticsearch(hosts, **es_config)
        self.client.ping()
        logger.debug("Elasticsearch client initialized")

    def close(self):
        logger.debug("Closing elasticsearch client ...")
        self.client = None
        logger.debug("Elasticsearch client closed")

    def get_query_builder(self):
        return ElasticsearchQueryBuilder()

    def get_bulk_writer(self, index:str, resource_type: ResourceType, max_buf_len: int = MAX_POST_DATA_LEN):
        return ElasticsearchBulkWriter(self, index, resource_type, max_buf_len)

    def create_index(self, index, config=None):
        logger.info("Creating index '%s' ...", index)
        self.client.indices.create(index, config, update_all_types=True)

    def delete_index(self, index):
        logger.info("Deleting index '%s' ...", index)
        self.client.indices.delete(index)

    def index_exists(self, index):
        return self.client.indices.exists(index)

    def get_doc(self, index, doc_type, doc_id):
        try:
            self.client.get(index, doc_id, doc_type)
        except elasticsearch.exceptions.TransportError as e:
            if e.status_code == 404:
                raise exceptions.NotFoundError("Document not found: {}".format(doc_id), doc_id)
            else:
                raise

    def create_doc(self, index, doc_type, doc_id, body):
        try:
            self.client.create(index, doc_type, doc_id, body)
        except elasticsearch.exceptions.TransportError as e:
            if e.status_code == 409:
                raise exceptions.AlreadyExistsError("Document already exists: {}".format(doc_id), doc_id)
            else:
                raise

    def update_doc(self, index, doc_type, doc_id, body):
        try:
            self.client.update(index, doc_type, doc_id, body)
        except elasticsearch.exceptions.TransportError as e:
            if e.status_code == 409:
                raise exceptions.AlreadyExistsError("Document already exists: {}".format(doc_id), doc_id)
            else:
                raise

    def create_or_update_doc(self, index, doc_type, doc_id, body):
        try:
            self.client.index(index, doc_type, body, doc_id)
        except elasticsearch.exceptions.TransportError as e:
            if e.status_code == 409:
                raise exceptions.AlreadyExistsError("Document already exists: {}".format(doc_id), doc_id)
            else:
                raise

    def delete_doc(self, index, doc_type, doc_id):
        try:
            self.client.delete(index, doc_type, doc_id)
        except elasticsearch.exceptions.TransportError as e:
            if e.status_code == 404:
                raise exceptions.NotFoundError("Document not found: {}".format(doc_id), doc_id)
            else:
                raise

    def count(self, index: str, doc_type: str, query: dict):
        logger.debug("Elasticsearch count: index='%s', doc_type='%s', body=%s",
                     index, doc_type, json.dumps(query, indent=2))
        result = self.client.count(index, doc_type, body=query)
        #logger.debug("Query results: %s", json.dumps(result, indent=2))
        return result['count']

    def count_time_series(self, index: str, doc_type: str, query: dict):
        logger.debug("Elasticsearch count time_series: index='%s', doc_type='%s', body=%s",
                     index, doc_type, json.dumps(query, indent=2))
        results = self.client.search(index, doc_type, body=query, size=0)
        #logger.debug("Query results: %s", json.dumps(results, indent=2))
        return [[result['key'], result['doc_count']] for result in results['aggregations']['time_series']['buckets']]

    def find(self, index: str, doc_type: str,
             filter_: dict, fields: list=None, sort: list=None,
             skip: int=0, limit: int=None, op='term'):
        if limit is None:
            limit = ElasticsearchClient.DEFAULT_SEARCH_SIZE

        query = self._get_query(filter_, op)
        results = self.client.search(
            index, doc_type, body=query,
            _source_include=fields, sort=sort,
            from_=skip, size=limit)
        return [x['_source'] for x in results['hits']['hits']]

    def scan(self, index: str, doc_type: str, query: dict, size=None):
        if size is None:
            size = ElasticsearchClient.DEFAULT_SCROLL_SIZE

        logger.debug("Elasticsearch scan: index='%s', doc_type='%s', body=%s",
                     index, doc_type, json.dumps(query, indent=2))
        page = self.client.search(index, doc_type, body=query, size=size)
        total = page['hits']['total']
        if total <= size:
            results = page['hits']['hits']
            for result in results:
                yield result['_source']
        else:
            # Use the scroll instead
            page = self.client.search(
                index, doc_type, body=query,
                scroll='5m', search_type='scan', size=size)

            scroll_id = page['_scroll_id']
            result_count = page['hits']['total']
            while result_count > 0:
                page = self.client.scroll(scroll_id, scroll='5m')
                scroll_id = page['_scroll_id']
                results = page['hits']['hits']
                result_count = len(results)

                for result in results:
                    yield result['_source']

#
#   Protected methods
#
    def _search(self,
             index: str, doc_type: str,
             query: dict, fields: list=None, sort: list=None,
             skip: int=0, limit: int=None):
        if limit is None:
            limit = ElasticsearchClient.DEFAULT_SEARCH_SIZE

        results = self.client.search(
            index, doc_type, body=query,
            _source_include=fields, sort=sort,
            from_=skip, size=limit)
        return [x['_source'] for x in results['hits']['hits']]

    def _bulk(self, db_name, doc_type, body):
        result = self.client.bulk(
            index=db_name,
            doc_type=doc_type,
            body=body,
            refresh=True,
            request_timeout=ElasticsearchClient.REQUEST_TIMEOUT)

        if result['errors'] is True:
            if 'items' in result:
                errors = []
                for item in result['items']:
                    error = None
                    if 'create' in item:
                        error = item['create']
                    elif 'index' in item:
                        error = item['index']
                    elif 'update' in item:
                        error = item['update']
                    elif 'delete' in item:
                        error = item['delete']

                    if error is not None:
                        errors.append(error)

                raise ElasticsearchBulkError(
                    total=len(result['items']),
                    in_error=len(errors),
                    errors=errors)
            else:
                raise ElasticsearchBulkError(
                    total=0,
                    in_error=0,
                    errors=[])

    def _get_query(self, filter_, op):
        if not filter_:
            return {
                "query": {
                    "match_all": {}
                }
            }

        return {
            "query": {
                "bool": {
                    "must": [{ op: { k: v }} for k, v in filter_.items()]
                }
            }
        }

    @staticmethod
    def _remove_sensitive_info(config):
        new_config = config.copy()
        new_config.pop('http_auth', None)
        return new_config


class BluemixElasticsearchClient(ElasticsearchClient):
    def __init__(self, url, username, password):
        logger.info("Initializing bluemix elasticsearch client: url=%s ...", url)

        parts = parse.urlparse(url)
        if parts.netloc:
            host_port = parts.netloc.split(':')
        elif parts.path:
            host_port = parts.path.split(':')
        else:
            raise ValueError("Invalid 'public_hostname' value: {}".format(url))

        es_conf = {
            "hosts": [host_port[0]],
            "port": int(host_port[1]),
            "http_auth": (username, password),
            "use_ssl": True,
            "verify_certs": True
        }

        super().__init__(es_conf)
        logger.info("Bluemix elasticsearch client initialized")

    @staticmethod
    def from_config(config):
        return BluemixElasticsearchClient(
            config['public_hostname'],
            config['username'],
            config['password'])
