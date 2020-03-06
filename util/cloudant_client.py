# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import cloudant
from cloudant.error import CloudantDatabaseException
from cloudant.document import Document
from http import HTTPStatus
import logging
import requests
import isodate
import datetime
import copy
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
        self.client = cloudant.Cloudant(self.username, self.auth_token, url=self.url, connect=True, auto_renew=True)
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

    def getDetailsById(self, account_id, provider_id, list):
        query = {
            "context.account_id": account_id,
            "provider_id": provider_id,
            "id": []
        }
        for note_id in list:
            query["id"].append(note_id)
        return self.find(key_values=query, fields=["_id", "_rev", "id"], index="ALL_FIELDS").docs
    
    def bulk_delete(self, request: list):
        response = []
        bulkResponse = self.db.bulk_docs(request)
        for result in bulkResponse:
            if "ok" in result:
                response.append({"id": result['id'], "result": "deleted successfully"})
            else:
                response.append({"id": result['id'], "result": "error occurred while deleting"})
        return response

    def create_doc(self, doc_id, body):
        try:
            create_body = copy.copy(body)
            if 'create_time' in create_body:
                create_datetime = isodate.parse_datetime(create_body['create_time'])
                create_timestamp = create_datetime.timestamp()
            else:
                create_datetime = datetime.datetime.utcnow()
                create_timestamp = create_datetime.timestamp()
                create_body['create_time'] = create_datetime.isoformat() + 'Z'
            create_body['create_timestamp'] = int(round(create_timestamp * 1000))
            create_body['insertion_timestamp'] = int(round(datetime.datetime.utcnow().timestamp() * 1000))
            create_body['_id'] = doc_id
            return self.db.create_document(create_body, throw_on_exists=True)
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
        else:
            ddoc.update_view(view_name, map_func, reduce_func, **kwargs)
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

        if sort:
            kwargs['sort'] = sort

        if limit:
            kwargs['limit'] = limit

        if bookmark:
            kwargs['bookmark'] = bookmark

        selector = CloudantDatabase._get_selector(key_values)
        result = self._get_query_result(selector, index, fields, **kwargs)
        bookmark = result.get('bookmark')
        if len(result['docs']) == 0:
            bookmark = ""
        return QueryResult(result['docs'], 0, bookmark)

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
