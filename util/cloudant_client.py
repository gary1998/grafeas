import cloudant
from cloudant.error import CloudantDatabaseException
from cloudant.document import Document
from http import HTTPStatus
import logging
import requests
from util import exceptions


logger = logging.getLogger("grafeas.cloudant_client")


class QueryResult(object):
    def __init__(self, docs, total_docs, bookmark):
        self.docs = docs
        self.total_docs = total_docs
        self.bookmark = bookmark


class CloudantDatabase(object):
    LUCENE_ESCAPE_RULES = {
        '+': r'\+',
        '-': r'\-',
        '&': r'\&',
        '|': r'\|',
        '!': r'\!',
        '(': r'\(',
        ')': r'\)',
        '{': r'\{',
        '}': r'\}',
        '[': r'\[',
        ']': r'\]',
        '^': r'\^',
        '~': r'\~',
        '*': r'\*',
        '?': r'\?',
        ':': r'\:',
        '"': r'\"',
        ';': r'\;',
        ' ': r'\ '
    }

    def __init__(self, url, db_name, username, auth_token):
        self.url = url
        self.db_name = db_name
        self.username = username
        self.auth_token = auth_token
        self._connect()

    def _connect(self):
        self.client = cloudant.Cloudant(self.username, self.auth_token, url=self.url, connect=True)
        self.db = self.client.get(self.db_name, remote=True)
        logger.debug("Cloudant client connected: url='%s', user='%s'", self.url, self.username)

    def _disconnect(self):
        try:
            self.client.disconnect()
        except requests.exceptions.HTTPError:
            logger.exception(
                "An error was encountered while disconnecting cloudant client: url='%s', user='%s'",
                self.url,
                self.username)

    def _reconnect(self):
        self._disconnect()
        self._connect()

    def get_doc(self, doc_id):
        doc = Document(self.db, doc_id)
        if not doc.exists():
            raise exceptions.NotFoundError("Document not found: {}".format(doc_id), doc_id)

        doc.fetch()
        return doc

    def create_doc(self, doc_id, body):
        try:
            body['_id'] = doc_id
            return self.db.create_document(body, throw_on_exists=True)
        except CloudantDatabaseException as e:
            if e.status_code == HTTPStatus.CONFLICT:
                raise exceptions.AlreadyExistsError("Document already exists: {}".format(doc_id), doc_id)
            else:
                raise

    def update_doc(self, doc_id, body):
        doc = Document(self.db, doc_id)
        if not doc.exists():
            raise exceptions.NotFoundError("Document not found: {}".format(doc_id), doc_id)

        doc.fetch()
        doc.update(body)
        doc.save()
        return doc

    def delete_doc(self, doc_id):
        doc = Document(self.db, doc_id)
        if not doc.exists():
            raise exceptions.NotFoundError("Document not found: {}".format(doc_id), doc_id)

        doc.fetch()
        doc.delete()
        return doc

    def create_query_index(self, index_name, fields, index_type='json'):
        ddoc = self.db.get_design_document("_design/" + index_name)
        if not ddoc.exists():
            self.db.create_query_index(
                design_document_id=index_name,
                index_name=index_name,
                index_type=index_type,
                fields=fields)

    def add_view(self, ddoc_id, view_name, map_func, reduce_func=None, **kwargs):
        ddoc = self.db.get_design_document("_design/" + ddoc_id)
        if not ddoc.exists() or view_name not in ddoc.views:
            ddoc.add_view(view_name, map_func, reduce_func, **kwargs)
            ddoc.save()

    def get_view(self, ddoc_id, view_name):
        ddoc = self.db.get_design_document("_design/" + ddoc_id)
        view = ddoc.get_view(view_name)
        return view

    def all_docs(self, include_docs: bool=False, skip: int=0, limit: int=0):
        view = self.db.all_docs(
            include_docs=include_docs,
            skip=skip,
            limit=limit)
        return view['rows']

    #
    # FIND
    #

    def find(self, key_values: dict, index: str, fields: list=None, sort: list=None,
             limit: int=None, bookmark: str=None):
        kwargs = {}

        if sort is not None:
            kwargs['sort'] = sort

        if limit is not None:
            kwargs['limit'] = limit

        if bookmark != 0:
            kwargs['bookmark'] = bookmark

        selector = CloudantDatabase._get_selector(key_values)
        result = self._get_query_result(selector, index, fields, **kwargs)
        return QueryResult(result['docs'], 0, result.get('bookmark'))

    def _get_query_result(self, selector: dict, index: str, fields=None, **kwargs):
            try:
                return self.db.get_query_result(
                    selector,
                    fields,
                    raw_result=True,
                    use_index=index,
                    **kwargs)
            except requests.exceptions.HTTPError as e:
                logger.exception(
                    "An error was encountered while getting query result: url='%s', user='%s', request-body=%s",
                    self.url,
                    self.username,
                    e.request.body)
                self._reconnect()
                return self.db.get_query_result(
                    selector,
                    fields,
                    raw_result=True,
                    use_index=index,
                    **kwargs)

    @staticmethod
    def _get_selector(key_values: dict):
        selector = {}
        for key, value in key_values.items():
            if isinstance(value, list):
                selector[key] = {"$in": value}
            else:
                selector[key] = {"$eq": value}
        return selector

    #
    # SEARCH API
    #

    def search(self, key_values: dict, index: str, fields: list=None, sort: list=None,
               limit: int=None, bookmark: str=None):
        query = CloudantDatabase._get_lucene_query(key_values)
        result = self._get_search_result(query, index, fields, sort, limit, bookmark)
        return QueryResult([row['doc'] for row in result['rows']], result['total_rows'], result.get('bookmark'))

    def _get_search_result(self, query: str, index: str, fields=None, sort: list=None,
                           limit: int=None, bookmark: str=None):
        ddoc_id, index = index.split('/')

        try:
            query_params = {}

            if fields:
                query_params['include_fields'] = fields

            if sort:
                query_params['sort'] = sort

            if limit:
                query_params['limit'] = limit

            if bookmark:
                query_params['bookmark'] = bookmark

            return self.db.get_search_result(
                '_design/' + ddoc_id,
                index,
                query=query,
                include_docs=True,
                **query_params)
        except requests.exceptions.HTTPError as e:
            logger.exception(
                "An error was encountered while getting query result: url='%s', user='%s', request-body=%s",
                self.client.url,
                self.client.username,
                e.request.body)
            self._reconnect()
            return self.db.get_search_result(
                '_design/' + ddoc_id,
                index,
                query=query,
                include_docs=True,
                **query_params)

    @staticmethod
    def _get_lucene_query(key_values: dict):
        query = []
        for key, value in key_values.items():
            if isinstance(value, list):
                values = list()
                values.append("(")
                for elem in value:
                    values.append(CloudantDatabase._escape_lucene_value(elem))
                    values.append(" OR ")
                values.pop() # remove last OR
                values.append(")")
                query.append("{}:{}".format(key, "".join(values)))
            else:
                query.append("{}:{}".format(key, CloudantDatabase._escape_lucene_value(value)))
            query.append(" AND ")

        query.pop() # remove last AND
        return "".join(query)

    @staticmethod
    def _escape_lucene_value(value):
        def get_next_char(s):
            for c in s:
                yield CloudantDatabase.LUCENE_ESCAPE_RULES.get(c, c)

        if isinstance(value, str):
            return "\"{}\"".format(value)
            #value = value.replace('\\', r'\\')  # escape \ first
            #return "\"{}\"".format("".join([c for c in get_next_char(value)]))

        if isinstance(value, bool):
            return "true" if value else "false"

        return value
