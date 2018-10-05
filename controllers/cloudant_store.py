# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import logging
import os
from controllers import common
from controllers import store
from util import cloudant_client
from util import exceptions
import time
import math

logger = logging.getLogger("grafeas.cloundant_store")


class CloudantStore(store.Store):
    def __init__(self):
        logger.info("Initializing DB client ...")
        self.db = CloudantStore._init_db()
        logger.info("DB client initialized.")

    #
    # Providers
    #

    def list_providers(self, author, account_id, filter_, page_size, page_token):
        view = self.db.get_view('doc_counts', "doc_count_by_provider")
        start_key = [account_id]
        end_key = [account_id, "\ufff0"]
        providers = []
        for row in view(startkey=start_key, endkey=end_key, group=True, group_level=2)['rows']:
            provider_id = row['key'][1]
            providers.append({
                'id': provider_id,
                'name': common.build_provider_name(account_id, provider_id)
            })

        return cloudant_client.QueryResult(providers, None, None)

    #
    # Notes
    #

    def write_note(self, author, account_id, provider_id, note_id, body, mode):
        note_name = common.build_note_name(account_id, provider_id, note_id)

        if mode == 'create':
            doc = self.db.create_doc(note_name, body)
        elif mode == 'update':
            doc = self.db.update_doc(note_name, body)
        else:
            raise ValueError("Invalid write note mode: {}".format(mode))

        return CloudantStore._clean_doc(doc)

    def get_note(self, author, account_id, provider_id, note_id):
        note_name = common.build_note_name(account_id, provider_id, note_id)
        doc = self.db.get_doc(note_name)
        return CloudantStore._clean_doc(doc)

    def list_notes(self, author, account_id, provider_id, filter_, page_size, page_token):
        provider_name = common.build_provider_name(account_id, provider_id)
        result = self.db.find(
            key_values={
                # 'author.account_id': author.account_id,
                'context.account_id': account_id,
                'doc_type': 'Note',
                'provider_name': provider_name
            },
            index="ALL_FIELDS",
            limit=page_size,
            bookmark=page_token)
        result.docs = [CloudantStore._clean_doc(doc) for doc in result.docs]
        return result

    def delete_note(self, author, account_id, provider_id, note_id):
        note_name = common.build_note_name(account_id, provider_id, note_id)
        self.db.delete_doc(note_name)

    #
    # Occurrences
    #

    def write_occurrence(self, author, account_id, provider_id, occurrence_id, body, mode):
        occurrence_name = common.build_occurrence_name(
            account_id, provider_id, occurrence_id)
        body = CloudantStore._internalize_occurrence(body)

        if mode == 'create':
            doc = self.db.create_doc(occurrence_name, body)
        elif mode == 'update':
            doc = self.db.update_doc(occurrence_name, body)
        elif mode == 'replace':
            try:
                doc = self.db.create_doc(occurrence_name, body)
            except exceptions.AlreadyExistsError:
                doc = self.db.update_doc(occurrence_name, body)
        else:
            raise ValueError("Invalid write occurrence mode: {}".format(mode))

        return CloudantStore._clean_occurrence(doc)

    def get_occurrence(self, author, account_id, provider_id, occurrence_id):
        occurrence_name = common.build_occurrence_name(
            account_id, provider_id, occurrence_id)
        doc = self.db.get_doc(occurrence_name)
        return CloudantStore._clean_occurrence(doc)

    def list_occurrences(self, author, account_id, provider_id, key_values, page_size, page_token):
        provider_name = common.build_provider_name(account_id, provider_id)
        result = self.db.find(
            key_values={
                # 'author.account_id': author.account_id,
                'context.account_id': account_id,
                'doc_type': 'Occurrence',
                'provider_name': provider_name
            },
            index="ALL_FIELDS",
            limit=page_size,
            bookmark=page_token)
        result.docs = [CloudantStore._clean_occurrence(
            doc) for doc in result.docs]
        return result

    def list_note_occurrences(self, author, account_id, provider_id, note_id, key_values, page_size, page_token):
        note_name = common.build_note_name(account_id, provider_id, note_id)
        result = self.db.find(
            key_values={
                # 'author.account_id': author.account_id,
                'context.account_id': account_id,
                'doc_type': 'Occurrence',
                'note_name': note_name
            },
            index="ALL_FIELDS",
            limit=page_size,
            bookmark=page_token)
        result.docs = [CloudantStore._clean_occurrence(
            doc) for doc in result.docs]
        return result

    def delete_occurrence(self, author, account_id, provider_id, occurrence_id):
        occurrence_name = common.build_occurrence_name(
            account_id, provider_id, occurrence_id)
        return self.db.delete_doc(occurrence_name)

    def delete_account_occurrences(self, author, account_id, start_time, end_time, count):
        page_size = int(os.environ.get('DELETE_OCCURRENCES_PAGE_SIZE', '200'))
        if count is not None:
            if count <= 0:
                return
            if count <= page_size:
                page_size = count
        total_deleted_count = 0
        view = self.db.get_view('doc_counts', "occurrence_count_by_utc")
        if start_time is None:
            start_time = -1
        if end_time is None:
            end_time = int(time.time() * 1000)
        # Set limit 1 greater than number of records to proccess in each batch
        # to know if more records are there and proccess them in next batch
        options = {
            "reduce": False,
            "limit": page_size + 1,
            "startkey": [account_id, start_time],
            "endkey": [account_id, end_time],
        }
        while True:
            limit = options["limit"]
            rows = view(**options)['rows']
            if len(rows) == limit:
                records_to_delete = rows[:limit - 1]
            else:
                records_to_delete = rows
            if len(records_to_delete) == 0:
                break
            deleted_docs = list(map(lambda x: {
                                '_deleted': True, '_id': x['id'], '_rev': x['value']}, records_to_delete))
            if deleted_docs:
                self.db.db.bulk_docs(deleted_docs)
            total_deleted_count += len(deleted_docs)
            if count is not None:
                remaining_count = count - total_deleted_count
                if remaining_count == 0:
                    break
                if remaining_count < limit:
                    options["limit"] = remaining_count + 1
            if len(rows) > limit - 1:
                options["startkey"] = rows[limit - 1]["key"]
            else:
                break
        logger.debug("%d occurrences deleted for account '%s': author account='%s'",
                     total_deleted_count, account_id, author.account_id)
        return total_deleted_count

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
            os.environ['CLOUDANT_URL'],
            os.environ['GRAFEAS_DB_NAME'],
            os.environ['CLOUDANT_USERNAME'],
            os.environ['CLOUDANT_PASSWORD'])

        db.create_query_index(
            'ALL_FIELDS',
            [],
            'text')
        # required by Legato's Query.occurrenceCount
        db.create_query_index(
            'RAI_DT_K',
            ['context.account_id', 'doc_type', 'kind'])
        # required by Legato's Card.findingCount
        db.create_query_index(
            'RAI_DT_K_NDI',
            ['context.account_id', 'doc_type', 'kind', 'note_name'])
        # required by Legato's Card.get_configured_card_occurrences
        db.create_query_index(
            'RAI_DT_K_PDI',
            ['context.account_id', 'doc_type', 'kind', 'provider_name'])
        # required by Legato's Card.findingCount
        db.create_query_index(
            'RAI_DT_K_PDI_NDI',
            ['context.account_id', 'doc_type', 'kind', 'provider_name', 'note_name'])

        db.add_view(
            'doc_counts',
            'doc_count_by_provider',
            """
            function(doc) {{
                if (doc.provider_id) {{
                    emit([doc.context.account_id, doc.provider_id], 1);
                }}
            }}
            """,
            '_sum')

        # 2018-04-15T16:30:00
        db.add_view(
            'doc_counts',
            'occurrence_count_by_date_time',
            """
            function(doc) {{
                if (doc.doc_type == "Occurrence") {{
                    emit([doc.context.account_id, doc.kind, doc.note_name,
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
            'doc_counts',
            'occurrence_count_by_week_date',
            """
            function(doc) {{
                if (doc.doc_type == "Occurrence") {{
                    emit([doc.context.account_id, doc.kind, doc.note_name,
                        parseInt(doc.update_week_date.substring(0, 4), 10),
                        parseInt(doc.update_week_date.substring(6, 8), 10),
                        parseInt(doc.update_week_date.substring(9, 10), 10)],
                        1);
                }}
            }}
            """,
            '_sum')

        db.add_view(
            'doc_counts',
            'occurrence_count_by_utc',
            """
            function(doc) {{
                if (doc.doc_type == "Occurrence") {{
                    emit([doc.context.account_id, doc.create_timestamp],null);
                }}
            }}
            """,
            '_count')

        return db
