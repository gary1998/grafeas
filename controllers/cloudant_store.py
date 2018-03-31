import logging
import os
from controllers import common
from controllers import store
from util import cloudant_client
from util import exceptions


logger = logging.getLogger("grafeas.cloundant_store")


class CloudantStore(store.Store):
    def __init__(self):
        logger.info("Initializing DB client ...")
        self.db = CloudantStore._init_db()
        logger.info("DB client initialized.")

    #
    # Projects
    #

    def create_project(self, subject_account_id, project_id, body):
        project_full_name = common.build_project_full_name(subject_account_id, project_id)
        doc = self.db.create_doc(project_full_name, body)
        return CloudantStore._clean_doc(doc)

    def get_project(self, subject_account_id, project_id):
        project_full_name = common.build_project_full_name(subject_account_id, project_id)
        doc = self.db.get_doc(project_full_name)
        return CloudantStore._clean_doc(doc)

    def list_projects(self, subject_account_id, filter_, page_size, page_token):
        docs = self.db.find(
            filter_={
                'account_id': subject_account_id,
                'doc_type': 'Project'
            },
            index="SAI_DT")
        return [CloudantStore._clean_doc(doc) for doc in docs]

    def delete_project(self, subject_account_id, project_id):
        project_full_name = common.build_project_full_name(subject_account_id, project_id)
        self.db.delete_doc(project_full_name)

    #
    # Notes
    #

    def write_note(self, subject_account_id, project_id, note_id, body, mode):
        note_full_name = common.build_note_full_name(subject_account_id, project_id, note_id)

        if mode == 'create':
            doc = self.db.create_doc(note_full_name, body)
        elif mode == 'update':
            doc = self.db.update_doc(note_full_name, body)
        else:
            raise ValueError("Invalid write note mode: {}".format(mode))

        return CloudantStore._clean_doc(doc)

    def get_note(self, subject_account_id, project_id, note_id):
        note_full_name = common.build_note_full_name(subject_account_id, project_id, note_id)
        doc = self.db.get_doc(note_full_name)
        return CloudantStore._clean_doc(doc)

    def list_notes(self, subject_account_id, project_id, filter_, page_size, page_token):
        project_full_name = common.build_project_full_name(subject_account_id, project_id)
        docs = self.db.find(
            filter_={
                'account_id': subject_account_id,
                'doc_type': 'Note',
                'project_doc_id': project_full_name
            },
            index="SAI_DT_PDI")
        return [CloudantStore._clean_doc(doc) for doc in docs]

    def delete_note(self, subject_account_id, project_id, note_id):
        note_full_name = common.build_note_full_name(subject_account_id, project_id, note_id)
        self.db.delete_doc(note_full_name)

    #
    # Occurrences
    #

    def write_occurrence(self, subject_account_id, project_id, occurrence_id, body, mode):
        occurrence_full_name = common.build_occurrence_full_name(subject_account_id, project_id, occurrence_id)
        body = CloudantStore._internalize_occurrence(body)

        if mode == 'create':
            doc = self.db.create_doc(occurrence_full_name, body)
        elif mode == 'update':
            doc = self.db.update_doc(occurrence_full_name, body)
        elif mode == 'replace':
            try:
                doc = self.db.create_doc(occurrence_full_name, body)
            except exceptions.AlreadyExistsError:
                doc = self.db.update_doc(occurrence_full_name, body)
        else:
            raise ValueError("Invalid write occurrence mode: {}".format(mode))

        return CloudantStore._clean_occurrence(doc)

    def get_occurrence(self, subject_account_id, project_id, occurrence_id):
        occurrence_full_name = common.build_occurrence_full_name(subject_account_id, project_id, occurrence_id)
        doc = self.db.get_doc(occurrence_full_name)
        return CloudantStore._clean_occurrence(doc)

    def list_occurrences(self, subject_account_id, project_id, filter_, page_size, page_token):
        project_full_name = common.build_project_full_name(subject_account_id, project_id)
        docs = self.db.find(
            filter_={
                'account_id': subject_account_id,
                'doc_type': 'Occurrence',
                'project_doc_id': project_full_name
            },
            index="SAI_DT_PDI")
        return [CloudantStore._clean_occurrence(doc) for doc in docs]

    def list_note_occurrences(self, subject_account_id, project_id, note_id, filter_, page_size, page_token):
        project_full_name = common.build_project_full_name(subject_account_id, project_id)
        note_full_name = common.build_note_full_name(subject_account_id, project_id, note_id)
        docs = self.db.find(
            filter_={
                'account_id': subject_account_id,
                'doc_type': 'Occurrence',
                'project_doc_id': project_full_name,
                'note_doc_id': note_full_name
            },
            index="SAI_DT_PDI_NDI")
        return [CloudantStore._clean_occurrence(doc) for doc in docs]

    def delete_occurrence(self, subject_account_id, project_id, occurrence_id):
        occurrence_full_name = common.build_occurrence_full_name(subject_account_id, project_id, occurrence_id)
        return self.db.delete_doc(occurrence_full_name)

    def delete_account_occurrences(self, resource_account_id):
        docs = self.db.find(
            filter_={
                'context.account_id': resource_account_id,
                'doc_type': 'Occurrence'
            },
            index="RAI_DT",
            fields=['_id'])

        for doc in docs:
            occurrence_full_name = doc['_id']
            self.db.delete_doc(occurrence_full_name)

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
        CloudantStore._externalize_occurrence(doc)
        return doc

    @staticmethod
    def _internalize_occurrence(doc):
        kind = doc['kind']
        if kind != 'FINDING':
            return doc

        details = doc['finding']
        severity = details['severity']
        details['severity'] = CloudantStore._INTERNAL_LEVEL_MAP[severity]

        certainty = details.get('certainty')
        if certainty:
            details['certainty'] = CloudantStore._INTERNAL_LEVEL_MAP[certainty]
        return doc

    @staticmethod
    def _externalize_occurrence(doc):
        kind = doc['kind']
        if kind != 'FINDING':
            return doc

        details = doc['finding']
        severity = details['severity']
        details['severity'] = CloudantStore._EXTERNAL_LEVEL_MAP[severity]

        certainty = details.get('certainty')
        if certainty:
            details['certainty'] = CloudantStore._EXTERNAL_LEVEL_MAP[certainty]
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
    def _init_db():
        db = cloudant_client.CloudantDatabase(
            os.environ['GRAFEAS_URL'],
            os.environ['GRAFEAS_DB_NAME'],
            os.environ['GRAFEAS_USERNAME'],
            os.environ['GRAFEAS_PASSWORD'])

        db.create_query_index(
            'RAI_DT',
            ['context.account_id', 'doc_type'])
        db.create_query_index(
            'RAI_DT_K_NDI',
            ['context.account_id', 'doc_type', 'kind', 'note_doc_id'])
        db.create_query_index(
            'RAI_DT_K_NDI_TS',
            ['context.account_id', 'doc_type', 'kind', 'note_doc_id', 'update_timestamp'])
        db.create_query_index(
            'RAI_DT_K_PDI',
            ['context.account_id', 'doc_type', 'kind', 'project_doc_id'])
        db.create_query_index(
            'RAI_DT_K_PDI_NDI',
            ['context.account_id', 'doc_type', 'kind', 'project_doc_id', 'note_doc_id'])
        db.create_query_index(
            'RAI_DT_K_SEV_TS_NDI',
            ['context.account_id', 'doc_type', 'kind', 'finding.severity', 'update_timestamp', 'note_doc_id'])
        db.create_query_index(
            'RAI_DT_K_SEV_TS_PDI_NDI',
            ['context.account_id', 'doc_type', 'kind', 'finding.severity', 'update_timestamp',
             'project_doc_id', 'note_doc_id'])
        db.create_query_index(
            'RAI_DT_K_TS_NDI',
            ['context.account_id', 'doc_type', 'kind', 'update_timestamp', 'note_doc_id'])
        db.create_query_index(
            'RAI_DT_K_TS_PDI_NDI',
            ['context.account_id', 'doc_type', 'kind', 'update_timestamp', 'project_doc_id', 'note_doc_id'])
        db.create_query_index(
            'RAI_DT_NDI_K_TS',
            ['context.account_id', 'doc_type', 'note_doc_id', 'kind', 'update_timestamp'])
        db.create_query_index(
            'RAI_DT_PDI',
            ['context.account_id', 'doc_type', 'project_doc_id'])
        db.create_query_index(
            'RAI_DT_PDI_NDI',
            ['context.account_id', 'doc_type', 'project_doc_id', 'note_doc_id'])
        db.create_query_index(
            'SAI_DT',
            ['account_id', 'doc_type'])
        db.create_query_index(
            'SAI_DT_K_PDI_S',
            ['account_id', 'doc_type', 'kind', 'project_doc_id', 'shared'])
        db.create_query_index(
            'SAI_DT_PDI',
            ['account_id', 'doc_type', 'project_doc_id'])
        db.create_query_index(
            'SAI_DT_PDI_NDI',
            ['account_id', 'doc_type', 'project_doc_id', 'note_doc_id'])

        # 2018-04-15T16:30:00
        db.add_view(
            'time_series',
            'finding_count_by_date_time',
            """
            function(doc) {{
                if (doc.doc_type == "Occurrence" && doc.kind == 'FINDING') {{
                    emit([doc.context.account_id, doc.note_doc_id, 
                        parseInt(doc.update_time.substring(0, 4), 10),
                        parseInt(doc.update_time.substring(5, 7), 10), 
                        parseInt(doc.update_time.substring(8, 10), 10),
                        parseInt(doc.update_time.substring(11, 13), 10),
                        parseInt(doc.update_time.substring(14, 16), 10),
                        parseInt(doc.update_time.substring(17, 19), 10)],
                        1);
                }}
            }}
            """,
            '_sum')

        # 2018-W04-2
        db.add_view(
            'time_series',
            'finding_count_by_week_date',
            """
            function(doc) {{
                if (doc.doc_type == "Occurrence" && doc.kind == 'FINDING') {{
                    emit([doc.context.account_id, doc.note_doc_id, 
                        parseInt(doc.update_week_date.substring(0, 4), 10),
                        parseInt(doc.update_week_date.substring(6, 8), 10),
                        parseInt(doc.update_week_date.substring(9, 10), 10)],
                        1);
                }}
            }}
            """,
            '_sum')

        return db
