import logging
import os
from controllers import common
from controllers import store
from util import elasticsearch_client
from util import exceptions


logger = logging.getLogger("grafeas.cloundant_store")


GRAFEAS_INDEX = 'grafeas'

class ElasticsearchStore(store.Store):
    def __init__(self):
        logger.info("Initializing DB client ...")
        self.client = ElasticsearchStore._init_client()
        logger.info("DB client initialized.")

    #
    # Projects
    #

    def create_project(self, subject_account_id, account_id, project_id, body):
        project_full_name = common.build_project_full_name(account_id, project_id)
        doc = self.client.create_doc(GRAFEAS_INDEX, 'Project', project_full_name, body)
        return ElasticsearchStore._clean_doc(doc)

    def get_project(self, subject_account_id, account_id, project_id):
        project_full_name = common.build_project_full_name(account_id, project_id)
        doc = self.client.get_doc(GRAFEAS_INDEX, 'Project', project_full_name)
        return ElasticsearchStore._clean_doc(doc)

    def list_projects(self, subject_account_id, account_id, filter_, page_size, page_token):
        docs = self.client.find(
            GRAFEAS_INDEX, 'Project',
            {
                'account_id': subject_account_id,
                'context.account_id': account_id
            })
        return [ElasticsearchStore._clean_doc(doc) for doc in docs]

    def delete_project(self, subject_account_id, account_id, project_id):
        project_full_name = common.build_project_full_name(account_id, project_id)
        self.client.delete_doc(GRAFEAS_INDEX, 'Project', project_full_name)

    #
    # Notes
    #

    def write_note(self, subject_account_id, account_id, project_id, note_id, body, mode):
        note_full_name = common.build_note_full_name(account_id, project_id, note_id)

        if mode == 'create':
            doc = self.client.create_doc(GRAFEAS_INDEX, 'Note', note_full_name, body)
        elif mode == 'update':
            doc = self.client.update_doc(GRAFEAS_INDEX, 'Note', note_full_name, body)
        else:
            raise ValueError("Invalid write note mode: {}".format(mode))

        return ElasticsearchStore._clean_doc(doc)

    def get_note(self, subject_account_id, account_id, project_id, note_id):
        note_full_name = common.build_note_full_name(account_id, project_id, note_id)
        doc = self.client.get_doc(GRAFEAS_INDEX, 'Note', note_full_name)
        return ElasticsearchStore._clean_doc(doc)

    def list_notes(self, subject_account_id, account_id, project_id, filter_, page_size, page_token):
        project_full_name = common.build_project_full_name(account_id, project_id)
        docs = self.client.find(
            GRAFEAS_INDEX, 'Note',
            {
                'account_id': subject_account_id,
                'context.account_id': account_id,
                'project_doc_id': project_full_name
            })
        return [ElasticsearchStore._clean_doc(doc) for doc in docs]

    def delete_note(self, subject_account_id, account_id, project_id, note_id):
        note_full_name = common.build_note_full_name(account_id, project_id, note_id)
        self.client.delete_doc(GRAFEAS_INDEX, 'Note', note_full_name)

    #
    # Occurrences
    #

    def write_occurrence(self, subject_account_id, account_id, project_id, occurrence_id, body, mode):
        occurrence_full_name = common.build_occurrence_full_name(account_id, project_id, occurrence_id)
        body = ElasticsearchStore._internalize_occurrence(body)

        if mode == 'create':
            doc = self.client.create_doc(GRAFEAS_INDEX, 'Occurrence', occurrence_full_name, body)
        elif mode == 'update':
            doc = self.client.update_doc(GRAFEAS_INDEX, 'Occurrence', occurrence_full_name, body)
        elif mode == 'replace':
            try:
                doc = self.client.create_doc(GRAFEAS_INDEX, 'Occurrence', occurrence_full_name, body)
            except exceptions.AlreadyExistsError:
                doc = self.client.update_doc(occurrence_full_name, body)
        else:
            raise ValueError("Invalid write occurrence mode: {}".format(mode))

        return ElasticsearchStore._clean_occurrence(doc)

    def get_occurrence(self, subject_account_id, account_id, project_id, occurrence_id):
        occurrence_full_name = common.build_occurrence_full_name(account_id, project_id, occurrence_id)
        doc = self.client.get_doc(GRAFEAS_INDEX, 'Occurrence', occurrence_full_name)
        return ElasticsearchStore._clean_occurrence(doc)

    def list_occurrences(self, subject_account_id, account_id, project_id, filter_, page_size, page_token):
        project_full_name = common.build_project_full_name(account_id, project_id)
        docs = self.client.find(
            GRAFEAS_INDEX, 'Occurrence',
            {
                'account_id': subject_account_id,
                'context.account_id': account_id,
                'project_doc_id': project_full_name
            })
        return [ElasticsearchStore._clean_occurrence(doc) for doc in docs]

    def list_note_occurrences(self, subject_account_id, account_id, project_id, note_id, filter_, page_size, page_token):
        project_full_name = common.build_project_full_name(account_id, project_id)
        note_full_name = common.build_note_full_name(account_id, project_id, note_id)
        docs = self.client.find(
            GRAFEAS_INDEX, 'Occurrence',
            {
                'account_id': subject_account_id,
                'context.account_id': account_id,
                'project_doc_id': project_full_name,
                'note_doc_id': note_full_name
            })
        return [ElasticsearchStore._clean_occurrence(doc) for doc in docs]

    def delete_occurrence(self, subject_account_id, account_id, project_id, occurrence_id):
        occurrence_full_name = common.build_occurrence_full_name(account_id, project_id, occurrence_id)
        return self.client.delete_doc(GRAFEAS_INDEX, 'Occurrence', occurrence_full_name)

    def delete_account_occurrences(self, subject_account_id, account_id):
        docs = self.client.find(
            GRAFEAS_INDEX, 'Occurrence',
            {
                'context.account_id': account_id,
                'doc_type': 'Occurrence'
            },
            fields=['account_id', 'name'])

        for doc in docs:
            occurrence_full_name = doc['account_id'] + '/' + doc['name']
            self.client.delete_doc(occurrence_full_name)

    @staticmethod
    def _clean_doc(doc):
        doc.pop('_id', None)
        doc.pop('_rev', None)
        doc.pop('doc_type', None)
        doc.pop('account_id', None)
        return doc

    @staticmethod
    def _clean_occurrence(doc):
        doc.pop('_id', None)
        doc.pop('_rev', None)
        doc.pop('doc_type', None)
        doc.pop('account_id', None)

        # externalize the severity and certainty values
        ElasticsearchStore._externalize_occurrence(doc)
        return doc

    @staticmethod
    def _internalize_occurrence(doc):
        kind = doc['kind']
        if kind != 'FINDING':
            return doc

        details = doc['finding']
        severity = details['severity']
        details['severity'] = ElasticsearchStore._INTERNAL_LEVEL_MAP[severity]

        certainty = details.get('certainty')
        if certainty:
            details['certainty'] = ElasticsearchStore._INTERNAL_LEVEL_MAP[certainty]
        return doc

    @staticmethod
    def _externalize_occurrence(doc):
        kind = doc['kind']
        if kind != 'FINDING':
            return doc

        details = doc['finding']
        severity = details['severity']
        details['severity'] = ElasticsearchStore._EXTERNAL_LEVEL_MAP[severity]

        certainty = details.get('certainty')
        if certainty:
            details['certainty'] = ElasticsearchStore._EXTERNAL_LEVEL_MAP[certainty]
        return doc

    _INTERNAL_LEVEL_MAP = {
        'LOW': 1,
        'MEDIUM': 2,
        'HIGH': 3
    }

    _EXTERNAL_LEVEL_MAP = {
        1: 'LOW',
        2: 'MEDIUM',
        3: 'HIGH'
    }

    @staticmethod
    def _init_client():
        db = elasticsearch_client.ComposeElasticsearchClient(
            os.environ['GRAFEAS_URL'],
            os.environ['GRAFEAS_USERNAME'],
            os.environ['GRAFEAS_PASSWORD'])

        return db
