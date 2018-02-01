import cloudant
from cloudant.error import CloudantDatabaseException
from cloudant.document import Document
from http import HTTPStatus
import logging
import os
import requests


logger = logging.getLogger("swagger_server.store")


class Store(object):
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
            self.disconnect()
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
            raise KeyError(doc_id)

        doc.fetch()
        return doc

    def create_doc(self, doc_id, body):
        try:
            body['_id'] = doc_id
            return self.db.create_document(body, throw_on_exists=True)
        except CloudantDatabaseException as e:
            if e.status_code == HTTPStatus.CONFLICT:
                raise KeyError(doc_id)
            else:
                raise

    def update_doc(self, doc_id, body):
        doc = Document(self.db, doc_id)
        if not doc.exists():
            raise KeyError(doc_id)

        doc.fetch()
        doc.update(body)
        doc.save()
        return doc

    def delete_doc(self, doc_id):
        doc = Document(self.db, doc_id)
        if not doc.exists():
            raise KeyError(doc_id)

        doc.fetch()
        doc.delete()
        return doc

    def create_query_index(self, index_name, fields):
        ddoc = self.db.get_design_document("_design/" + index_name)
        if not ddoc.exists():
            self.db.create_query_index(
                design_document_id=index_name,
                index_name=index_name,
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

    def find(self, filter_: dict, index: str, fields: list = None, sort: list = None, skip: int = 0, limit: int = 0):
        kwargs = {}

        if skip != 0:
            kwargs['skip'] = skip

        if limit != 0:
            kwargs['limit'] = limit

        if sort is not None:
            kwargs['sort'] = sort

        selector = Store._get_selector(filter_)
        result = self._get_query_result(selector, index, fields, **kwargs)
        return result['docs']

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
                    self.client.url,
                    self.client.username,
                    e.request.body)
                self._reconnect()
                return self.db.get_query_result(
                    selector,
                    fields,
                    raw_result=True,
                    use_index=index,
                    **kwargs)

    @staticmethod
    def _get_selector(filter_: dict):
        selector = {}
        for name, value in filter_.items():
            selector[name] = {"$eq": value}
        return selector
