import datetime
import http
import isodate
import logging
import threading
from controllers import common
from util import exceptions
from util import dict_util


logger = logging.getLogger("grafeas.api")


class API(object):
    def __init__(self, store):
        self.store = store

    #
    #  Projects
    #

    def create_project(self, subject_account_id, body):
        project_id = body['id']
        common.validate_id(project_id)

        body['doc_type'] = 'Project'
        body['account_id'] = subject_account_id
        body['id'] = project_id
        body['name'] = common.build_project_name(project_id)

        if 'shared' not in body:
            body['shared'] = True

        return self.store.create_project(subject_account_id, project_id, body)

    def list_projects(self, subject_account_id, filter_, page_size, page_token):
        return self.store.list_projects(subject_account_id, filter_, page_size, page_token)

    def get_project(self, subject_account_id, project_id):
        return self.store.get_project(subject_account_id, project_id)

    def delete_project(self, subject_account_id, project_id):
        self.store.delete_project(subject_account_id, project_id)

    #
    #  Notes
    #

    def write_note(self, subject_account_id, project_id, note_id, body, mode='create'):
        common.validate_id(project_id)
        common.validate_id(note_id)

        project_full_name = common.build_project_full_name(subject_account_id, project_id)
        note_name = common.build_note_name(project_id, note_id)

        kind = body['kind']
        API._validate_kind_field(kind, body, API._NOTE_KIND_FIELD_NAME_MAP)

        body['doc_type'] = 'Note'
        body['id'] = note_id
        body['account_id'] = subject_account_id
        body['project_id'] = project_id
        body['project_doc_id'] = project_full_name
        body['name'] = note_name

        if 'create_time' in body:
            create_datetime = isodate.parse_datetime(body['create_time'])
            create_timestamp = create_datetime.timestamp()
        else:
            create_datetime = datetime.datetime.utcnow()
            create_timestamp = create_datetime.timestamp()
            body['create_time'] = create_datetime.isoformat() + 'Z'
        body['create_timestamp'] = int(round(create_timestamp * 1000))

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

        return self.store.write_note(subject_account_id, project_id, note_id, body, mode)

    def list_notes(self, subject_account_id, project_id, filter_, page_size, page_token):
        return self.store.list_notes(subject_account_id, project_id, filter_, page_size, page_token)

    def get_note(self, subject_account_id, project_id, note_id):
        return self.store.get_note(subject_account_id, project_id, note_id)

    def get_occurrence_note(self, subject_account_id, project_id, occurrence_id):
        occurrence_doc = self.store.get_occurrence(subject_account_id, project_id, occurrence_id)
        note_name = occurrence_doc['note_name']
        note_account_id, note_project_id, note_id = common.parse_note_name(note_name, subject_account_id)
        return self.store.get_note(note_account_id, note_project_id, note_id)

    def delete_note(self, subject_account_id, project_id, note_id):
        self.store.delete_note(subject_account_id, project_id, note_id)

    #
    #  Occurrences
    #

    def write_occurrence(self, subject_account_id, project_id, occurrence_id, body, mode='create'):
        common.validate_id(project_id)
        common.validate_id(occurrence_id)

        # verify note exists (a not-found exception will be raised if the note does not exist) and access is allowed
        note_name = body['note_name']
        note_account_id, note_project_id, note_id = common.parse_note_name(note_name, subject_account_id)
        note = self.store.get_note(note_account_id, note_project_id, note_id)
        if note_account_id != subject_account_id and not note['shared']:
            raise exceptions.JSONError.from_http_status(
                http.HTTPStatus.FORBIDDEN,
                "Occurrence's note is not shared: {}".format(note_name))

        kind = body['kind']
        self._validate_kind_field(kind, body, API._OCCURRENCE_KIND_FIELD_NAME_MAP)

        body['doc_type'] = 'Occurrence'
        body['account_id'] = subject_account_id
        body['project_id'] = project_id
        body['id'] = occurrence_id
        body['name'] = common.build_occurrence_name(project_id, occurrence_id)
        body['project_doc_id'] = common.build_project_full_name(subject_account_id, project_id)
        body['note_doc_id'] = common.build_note_full_name(note_account_id, note_project_id, note_id)

        if 'create_time' in body:
            create_datetime = isodate.parse_datetime(body['create_time'])
            create_timestamp = create_datetime.timestamp()
        else:
            create_datetime = datetime.datetime.utcnow()
            create_timestamp = create_datetime.timestamp()
            body['create_time'] = create_datetime.isoformat() + 'Z'
        body['create_timestamp'] = int(round(create_timestamp * 1000))

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
        return self.store.write_occurrence(subject_account_id, project_id, occurrence_id, body, mode)

    def list_occurrences(self, subject_account_id, project_id, filter_, page_size, page_token):
        return self.store.list_occurrences(subject_account_id, project_id, filter_, page_size, page_token)

    def list_note_occurrences(self, subject_account_id, project_id, note_id, filter_, page_size, page_token):
        return self.store.list_note_occurrences(subject_account_id, project_id, note_id, filter_, page_size, page_token)

    def get_occurrence(self, subject_account_id, project_id, occurrence_id):
        return self.store.get_occurrence(subject_account_id, project_id, occurrence_id)

    def delete_occurrence(self, subject_account_id, project_id, occurrence_id):
        self.store.delete_occurrence(subject_account_id, project_id, occurrence_id)

    def delete_account_occurrences(self, resource_account_id):
        self.store.delete_account_occurrences(resource_account_id)

    @staticmethod
    def _week_date_iso_format(iso_calendar):
        return "{:04d}-W{:02d}-{}".format(iso_calendar[0], iso_calendar[1], iso_calendar[2])

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


__api_impl = None
__api_impl_lock = threading.Lock()


def get_api_impl():
    from controllers import cloudant_store

    global __api_impl
    with __api_impl_lock:
        if __api_impl is None:
            __api_impl = API(cloudant_store.CloudantStore())
            try:
                __api_impl.write_note('system', 'core', 'card_configured', {
                    "kind": "CARD_CONFIGURED",
                    "short_description": "Used to indicate a card was configured for the user account",
                    "long_description": "Used to indicate a card was configured for the user account"
                })
            except exceptions.AlreadyExistsError:
                pass

            try:
                __api_impl.write_note('system', 'core', 'account_deleted', {
                    "kind": "ACCOUNT_DELETED",
                    "short_description": "Used to indicate a user account was deleted",
                    "long_description": "Used to indicate a user account was deleted"
                })
            except exceptions.AlreadyExistsError:
                pass

        return __api_impl
