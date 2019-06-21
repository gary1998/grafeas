# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import datetime
import http
import isodate
import logging
import threading
from controllers import common
from util import auth_util
from util import exceptions
from util import dict_util


logger = logging.getLogger("grafeas.api")


class API(object):
    def __init__(self, store):
        self.store = store

    #
    #  Providers
    #

    def list_providers(self, author, account_id, filter_, page_size, page_token):
        return self.store.list_providers(author,  account_id, filter_, page_size, page_token)

    #
    #  Notes
    #

    def write_note(self, author, account_id, provider_id, note_id, body, mode='create'):
        common.validate_id(provider_id)
        common.validate_id(note_id)

        kind = body['kind']
        API._validate_kind_field(kind, body, API._NOTE_KIND_FIELD_NAME_MAP)

        if kind == "CARD":
            section = body['card']['section']
            order = body['card']['order'] if 'order' in body['card'] else None
            result = self.store.list_section_card(author, account_id, provider_id, section)
            if account_id not in ["fa53b6717d5e9c9979101d8dac5fd4ad"]:
                API._validate_card_order(result.docs, section, order)
                API._validate_card_elements(body['card']['elements'])

        body['doc_type'] = 'Note'
        body['id'] = note_id
        body['author'] = author.to_dict()
        body['provider_id'] = provider_id
        body['provider_name'] = common.build_provider_name(account_id, provider_id)
        body['name'] = common.build_note_name(account_id, provider_id, note_id)
        common.set_context_account_id(body, account_id)

        if 'create_time' in body:
            create_datetime = isodate.parse_datetime(body['create_time'])
            create_timestamp = create_datetime.timestamp()
        else:
            create_datetime = datetime.datetime.utcnow()
            create_timestamp = create_datetime.timestamp()
            body['create_time'] = create_datetime.isoformat() + 'Z'
        body['create_timestamp'] = int(round(create_timestamp * 1000))
        body['insertion_timestamp'] = int(round(datetime.datetime.utcnow().timestamp() * 1000))

        if 'update_time' in body:
            update_datetime = isodate.parse_datetime(body['update_time'])
            update_timestamp = update_datetime.timestamp()
        else:
            update_datetime = datetime.datetime.utcnow()
            update_timestamp = update_datetime.timestamp()
            body['update_time'] = update_datetime.isoformat() + 'Z'
        body['update_timestamp'] = int(round(update_timestamp * 1000))
        body['update_week_date'] = API._week_date_iso_format(update_datetime.isocalendar())

        if 'shared' not in body:
            body['shared'] = True

        return self.store.write_note(author, account_id, provider_id, note_id, body, mode)

    def list_notes(self, author,  account_id, provider_id, filter_, page_size, page_token):
        return self.store.list_notes(author, account_id, provider_id, filter_, page_size, page_token)

    def get_note(self, author,  account_id, provider_id, note_id):
        return self.store.get_note(author, account_id, provider_id, note_id)

    def get_occurrence_note(self, author,  account_id, provider_id, occurrence_id):
        occurrence_doc = self.store.get_occurrence(author, account_id, provider_id, occurrence_id)
        note_name = occurrence_doc['note_name']
        note_account_id, note_provider_id, note_id = common.parse_note_name(note_name)
        return self.store.get_note(author, note_account_id, note_provider_id, note_id)

    def delete_note(self, author,  account_id, provider_id, note_id):
        self.store.delete_note(author, account_id, provider_id, note_id)

    #
    #  Occurrences
    #

    def write_occurrence(self, author, account_id, provider_id, occurrence_id, body, mode='create'):
        common.validate_id(provider_id)
        common.validate_id(occurrence_id)

        # verify note exists (a not-found exception will be raised if the note does not exist) and access is allowed
        note_name = body['note_name']
        note_account_id, note_provider_id, note_id = common.parse_note_name(note_name)
        note = self.store.get_note(author, note_account_id, note_provider_id, note_id)
        if note_account_id != account_id and not note['shared']:
            raise exceptions.JSONError.from_http_status(
                http.HTTPStatus.FORBIDDEN,
                "Occurrence's note is not shared: {}".format(note_name))

        kind = body['kind']
        self._validate_kind_field(kind, body, API._OCCURRENCE_KIND_FIELD_NAME_MAP)

        body['doc_type'] = 'Occurrence'
        body['author'] = author.to_dict()
        body['provider_id'] = provider_id
        body['id'] = occurrence_id
        body['name'] = common.build_occurrence_name(account_id, provider_id, occurrence_id)
        body['provider_name'] = common.build_provider_name(account_id, provider_id)
        body['note_name'] = common.build_note_name(note_account_id, note_provider_id, note_id)
        common.set_context_account_id(body, account_id)

        if 'create_time' in body:
            create_datetime = isodate.parse_datetime(body['create_time'])
            create_timestamp = create_datetime.timestamp()
        else:
            create_datetime = datetime.datetime.utcnow()
            create_timestamp = create_datetime.timestamp()
            body['create_time'] = create_datetime.isoformat() + 'Z'
        body['create_timestamp'] = int(round(create_timestamp * 1000))
        body['insertion_timestamp'] = int(round(datetime.datetime.utcnow().timestamp() * 1000))

        if 'update_time' in body:
            update_datetime = isodate.parse_datetime(body['update_time'])
            update_timestamp = update_datetime.timestamp()
        else:
            update_datetime = datetime.datetime.utcnow()
            update_timestamp = update_datetime.timestamp()
            body['update_time'] = update_datetime.isoformat() + 'Z'
        body['update_timestamp'] = int(round(update_timestamp * 1000))
        body['update_week_date'] = self._week_date_iso_format(update_datetime.isocalendar())

        self._set_occurrence_defaults(body, note)
        return self.store.write_occurrence(author, account_id, provider_id, occurrence_id, body, mode)

    def list_occurrences(self, author, account_id, provider_id, filter_, page_size, page_token):
        return self.store.list_occurrences(author, account_id, provider_id, filter_, page_size, page_token)

    def list_note_occurrences(self, author, account_id, provider_id, note_id, filter_, page_size, page_token):
        return self.store.list_note_occurrences(author, account_id, provider_id, note_id, filter_, page_size, page_token)

    def get_occurrence(self, author, account_id, provider_id, occurrence_id):
        return self.store.get_occurrence(author, account_id, provider_id, occurrence_id)

    def delete_occurrence(self, author, account_id, provider_id, occurrence_id):
        self.store.delete_occurrence(author, account_id, provider_id, occurrence_id)

    def delete_account_occurrences(self, author, account_id, start_time, end_time, count):
        return self.store.delete_account_occurrences(author, account_id, start_time, end_time, count)

    @staticmethod
    def _week_date_iso_format(iso_calendar):
        return "{:04d}-W{:02d}-{}".format(iso_calendar[0], iso_calendar[1], iso_calendar[2])

    @staticmethod
    def _validate_card_order(custom_section_cards, section, order):
        existing_sections = set()
        count_section_cards = 0
        for c in custom_section_cards:
            existing_sections.add(c['card']['section'])

        if section not in existing_sections:
            if len(existing_sections) >= API.MAX_ALLOWED_CUSTOM_SECTION and "Partner Integrations" not in existing_sections:
                raise exceptions.UnprocessableEntity(
                    "Max number of allowed sections per account are {}".format(
                        API.MAX_ALLOWED_CUSTOM_SECTION))
            if len(existing_sections) >= (API.MAX_ALLOWED_CUSTOM_SECTION + 1) and "Partner Integrations" in existing_sections:
                raise exceptions.UnprocessableEntity(
                    "Max number of allowed sections per account are {}".format(
                        API.MAX_ALLOWED_CUSTOM_SECTION))
        else:
            for section_card in custom_section_cards:
                if section == section_card['card']['section']:
                    if order and 'order' in section_card['card'] and order == section_card['card']['order']:
                        raise exceptions.AlreadyExistsError(
                            "Given order is already taken by other card in {} section".format(
                                section))

                    count_section_cards += 1

        if count_section_cards >= API.MAX_ALLOWED_CARDS_IN_CUSTOM_SECTION:
            raise exceptions.UnprocessableEntity(
                "Max number of allowed cards in a section are {}".format(
                        API.MAX_ALLOWED_CARDS_IN_CUSTOM_SECTION))

        if order and order > (count_section_cards + 1):
            raise exceptions.UnprocessableEntity(
                "Order of the card cannot be more than existing number of cards plus one ({}) in a section".format(
                    count_section_cards + 1))

    @staticmethod
    def _validate_card_elements(elements):
        kri_count = 0
        chart_count = 0
        for element in elements:
            if element['kind'] == 'NUMERIC':
                kri_count = kri_count + 1
            else:
                chart_count = chart_count + 1

        if chart_count == 0 and kri_count > API.MAX_KRI_ELEMENTS:
            raise exceptions.UnprocessableEntity(
                "Invalid number of NUMERIC elements: Max {} NUMERIC elements are allowed".format(API.MAX_KRI_ELEMENTS))

        if chart_count == 1 and kri_count > int(API.MAX_KRI_ELEMENTS / 2):
            raise exceptions.UnprocessableEntity(
                "Invalid number of NUMERIC elements: Max {} NUMERIC elements are allowed along with a graph".format(int(API.MAX_KRI_ELEMENTS / 2)))

        if chart_count > API.MAX_CHART_ELEMENTS:
            raise exceptions.UnprocessableEntity(
                "Invalid number of TIME_SERIES/BREAKDOWN elements: Max allowed is {}".format(API.MAX_CHART_ELEMENTS))

    @staticmethod
    def _validate_kind_field(kind, body, map_):
        field_name = map_.get(kind)

        if field_name is None:
            raise exceptions.BadRequestError("Invalid kind: {}".format(kind))

        if field_name == API.KIND_NOT_SUPPORTED:
            raise exceptions.BadRequestError("Invalid kind: {}".format(kind))

        if field_name == API.FIELD_NOT_REQUIRED:
            return

        if field_name not in body:
            raise exceptions.BadRequestError("Missing field '{}' for kind '{}'".format(field_name, kind))

    @staticmethod
    def _set_occurrence_defaults(body, note):
        if 'short_description' not in body:
            body['short_description'] = note.get('short_description')
        if 'long_description' not in body:
            body['long_description'] = note.get('long_description')
        if 'reported_by' not in body:
            body['reported_by'] = note.get('reported_by')

        kind = body['kind']
        if kind == 'FINDING':
            merged_finding = dict_util.override(note['finding'], body['finding'])
            body['finding'] = merged_finding
        elif kind == 'KPI':
            merged_kpi = dict_util.override(note['kpi'], body['kpi'])
            body['kpi'] = merged_kpi

    FIELD_NOT_REQUIRED = "$NOT-REQUIRED"
    KIND_NOT_SUPPORTED = "$NOT-SUPPORTED"

    _NOTE_KIND_FIELD_NAME_MAP = {
        'FINDING': 'finding',
        'KPI': 'kpi',
        'CARD': 'card',
        'SECTION': 'section',
        'CARD_CONFIGURED': FIELD_NOT_REQUIRED,
        'ACCOUNT_DELETED': FIELD_NOT_REQUIRED
    }

    _OCCURRENCE_KIND_FIELD_NAME_MAP = {
        'FINDING': 'finding',
        'KPI': 'kpi',
        'CARD': KIND_NOT_SUPPORTED,
        'SECTION': KIND_NOT_SUPPORTED,
        'CARD_CONFIGURED': 'card_configured',
        'ACCOUNT_DELETED': FIELD_NOT_REQUIRED
    }

    MAX_KRI_ELEMENTS = 4
    MAX_CHART_ELEMENTS = 1
    MAX_ALLOWED_CUSTOM_SECTION = 3
    MAX_ALLOWED_CARDS_IN_CUSTOM_SECTION = 6


SYSTEM_AUTHOR = auth_util.Subject('service-id', '$SYSTEM-ID', '$SYSTEM-ACCOUNT-ID')


__api_impl = None
__api_impl_lock = threading.Lock()


def get_api_impl():
    from controllers import cloudant_store

    global __api_impl
    with __api_impl_lock:
        if __api_impl is None:
            __api_impl = API(cloudant_store.CloudantStore())
            try:
                __api_impl.write_note(SYSTEM_AUTHOR, 'system', 'core', 'card_configured', {
                    "kind": "CARD_CONFIGURED",
                    "short_description": "Used to indicate a card was configured for the user account",
                    "long_description": "Used to indicate a card was configured for the user account"
                })
            except exceptions.AlreadyExistsError:
                pass

            try:
                __api_impl.write_note(SYSTEM_AUTHOR, 'system', 'core', 'account_deleted', {
                    "kind": "ACCOUNT_DELETED",
                    "short_description": "Used to indicate a user account was deleted",
                    "long_description": "Used to indicate a user account was deleted"
                })
            except exceptions.AlreadyExistsError:
                pass

        return __api_impl
