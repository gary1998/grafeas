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
    def __init__(self, auth_client, store):
        self.auth_client = auth_client
        self.store = store

    #
    #  Projects
    #

    def create_project(self, request, body):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_write_projects(subject)
        project_id = body['id']
        body['doc_type'] = 'Project'
        body['account_id'] = subject.account_id
        body['id'] = project_id
        body['name'] = common.build_project_name(project_id)

        if 'shared' not in body:
            body['shared'] = True

        return self.store.create_project(subject.account_id, project_id, body)

    def list_projects(self, request, filter_, page_size, page_token):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_read_projects(subject)
        return self.store.list_projects(subject.account_id, filter_, page_size, page_token)

    def get_project(self, request, project_id):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_read_projects(subject)
        return self.store.get_project(subject.account_id, project_id)

    def delete_project(self, request, project_id):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_delete_projects(subject)
        self.store.delete_project(subject.account_id, project_id)

    #
    #  Notes
    #

    def write_note(self, request, project_id, note_id, body, mode='create'):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_write_notes(subject)
        project_doc_id = common.build_project_doc_id(subject.account_id, project_id)
        note_name = common.build_note_name(project_id, note_id)

        kind = body['kind']
        API._validate_note_kind(kind, body)

        body['doc_type'] = 'Note'
        body['id'] = note_id
        body['account_id'] = subject.account_id
        body['project_id'] = project_id
        body['project_doc_id'] = project_doc_id
        body['name'] = note_name

        if 'create_time' in body:
            create_datetime = isodate.parse_datetime(body['create_time'])
            create_timestamp = create_datetime.timestamp()
        else:
            create_datetime = datetime.datetime.utcnow()
            create_timestamp = create_datetime.timestamp()
            body['create_time'] = create_datetime.isoformat() + 'Z'
        body['create_timestamp'] = create_timestamp

        if 'update_time' in body:
            update_datetime = isodate.parse_datetime(body['update_time'])
            update_timestamp = update_datetime.timestamp()
        else:
            update_datetime = datetime.datetime.utcnow()
            update_timestamp = update_datetime.timestamp()
            body['update_time'] = update_datetime.isoformat() + 'Z'
        body['update_timestamp'] = update_timestamp
        body['update_week_date'] = API._week_date_iso_format(update_datetime.isocalendar())

        if 'shared' not in body:
            body['shared'] = True

        return self.store.write_note(subject.account_id, project_id, note_id, body, mode)

    def list_notes(self, request, project_id, filter_, page_size, page_token):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_read_notes(subject)
        return self.store.list_notes(subject.account_id, project_id, filter_, page_size, page_token)

    def get_note(self, request, project_id, note_id):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_read_notes(subject)
        return self.store.get_note(subject.account_id, project_id, note_id)

    def get_occurrence_note(self, request, project_id, occurrence_id):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_read_notes(subject)
        occurrence_doc = self.store.get_occurrence(subject.account_id, project_id, occurrence_id)
        note_name = occurrence_doc['note_name']
        note_name_parts = note_name.split('/')
        return self.store.get_note(subject.account_id, note_name_parts[1], note_name_parts[3])

    def delete_note(self, request, project_id, note_id):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_delete_notes(subject)
        self.store.delete_note(subject.account_id, project_id, note_id)

    #
    #  Occurrences
    #

    def write_occurrence(self, request, project_id, occurrence_id, body, mode='create'):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_write_occurrences(subject)
        project_doc_id = common.build_project_doc_id(subject.account_id, project_id)
        occurrence_name = common.build_occurrence_name(project_id, occurrence_id)
        note_name = body['note_name']

        # get the occurrence's note name parts
        try:
            if note_name.startswith("projects/"):
                # relative name
                note_name_parts = note_name.split('/')
                note_account_id = subject.account_id
                note_project_id = note_name_parts[1]
                note_id = note_name_parts[3]
            else:
                # absolute name
                note_name_parts = note_name.split('/')
                note_account_id = note_name_parts[0]
                note_project_id = note_name_parts[2]
                note_id = note_name_parts[4]
        except IndexError:
            raise exceptions.BadRequestError("Invalid note name: {}".format(note_name))

        # verify note exists (a not-found exception will be raised if the note does not exist)
        note = self.store.get_note(note_account_id, note_project_id, note_id)

        if not note_name.startswith("projects/") and not note['shared']:
            raise exceptions.JSONError.from_http_status(
                http.HTTPStatus.FORBIDDEN,
                "Occurrence's note is not shared: {}".format(note_name))

        kind = body['kind']
        self._validate_occurrence_kind(kind, body)

        resource = body['context']
        resource_account_id = resource['account_id']
        if resource_account_id != subject.account_id:
            self.auth_client.assert_can_write_occurrences_for_others(subject)

        body['doc_type'] = 'Occurrence'
        body['account_id'] = subject.account_id
        body['project_id'] = project_id
        body['id'] = occurrence_id
        body['name'] = occurrence_name
        body['project_doc_id'] = project_doc_id
        body['note_doc_id'] = common.build_note_doc_id(note_account_id, note_project_id, note_id)

        if 'create_time' in body:
            create_datetime = isodate.parse_datetime(body['create_time'])
            create_timestamp = create_datetime.timestamp()
        else:
            create_datetime = datetime.datetime.utcnow()
            create_timestamp = create_datetime.timestamp()
            body['create_time'] = create_datetime.isoformat() + 'Z'
        body['create_timestamp'] = create_timestamp

        if 'update_time' in body:
            update_datetime = isodate.parse_datetime(body['update_time'])
            update_timestamp = update_datetime.timestamp()
        else:
            update_datetime = datetime.datetime.utcnow()
            update_timestamp = update_datetime.timestamp()
            body['update_time'] = update_datetime.isoformat() + 'Z'
        body['update_timestamp'] = update_timestamp
        body['update_week_date'] = self._week_date_iso_format(update_datetime.isocalendar())

        self._set_occurrence_defaults(body, note)
        return self.store.write_occurrence(subject.account_id, project_id, occurrence_id, body, mode)

    def list_occurrences(self, request, project_id, filter_, page_size, page_token):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_read_occurrences(subject)
        return self.store.list_occurrences(subject.account_id, project_id, filter_, page_size, page_token)

    def list_note_occurrences(self, request, project_id, note_id, filter_, page_size, page_token):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_read_occurrences(subject)
        return self.store.list_note_occurrences(subject.account_id, project_id, note_id, filter_, page_size, page_token)

    def get_occurrence(self, request, project_id, occurrence_id):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_read_occurrences(subject)
        return self.store.get_occurrence(subject.account_id, project_id, occurrence_id)

    def delete_occurrence(self, request, project_id, occurrence_id):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_delete_occurrences(subject)
        self.store.delete_occurrence(subject.account_id, project_id, occurrence_id)

    def delete_all_account_data(self, request):
        subject = self.auth_client.get_subject(request)
        self.auth_client.assert_can_delete_occurrences(subject)
        self.store.delete_all_account_data(subject.account_id)

    @staticmethod
    def _week_date_iso_format(iso_calendar):
        return "{:04d}-W{:02d}-{}".format(iso_calendar[0], iso_calendar[1], iso_calendar[2])

    @staticmethod
    def _validate_note_kind(kind, body):
        field_name = API.NOTE_KIND_FIELD_NAME_MAP.get(kind)
        if field_name is None:
            raise exceptions.BadRquestError("Invalid note's kind: {}".format(kind))

        if field_name == 'NOT-REQUIRED':
            return

        if field_name not in body:
            raise exceptions.BadRquestError("Missing note's field '{}' for kind '{}'".format(field_name, kind))

    @staticmethod
    def _validate_occurrence_kind(kind, body):
        field_name = API.OCCURRENCE_KIND_FIELD_NAME_MAP.get(kind)
        if field_name is None:
            raise exceptions.BadRquestError("Invalid occurrence's kind: {}".format(kind))

        if field_name not in body:
            raise exceptions.BadRquestError("Missing occurrence's field '{}' for kind '{}'".format(field_name, kind))

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
            merged_finding = dict_util.dict_merge(note['finding'], body['finding'])
            body['finding'] = merged_finding
        elif kind == 'KPI':
            merged_kpi = dict_util.dict_merge(note['kpi'], body['kpi'])
            body['kpi'] = merged_kpi

    NOTE_KIND_FIELD_NAME_MAP = {
        'FINDING': 'finding',
        'KPI': 'kpi',
        'CARD': 'card',
        'CARD_CONFIGURED': 'NOT-REQUIRED'
    }

    OCCURRENCE_KIND_FIELD_NAME_MAP = {
        'FINDING': 'finding',
        'KPI': 'kpi',
        'CARD': 'card',
        'CARD_CONFIGURED': 'card_configured'
    }


__api_impl = None
__api_impl_lock = threading.Lock()


def get_api_impl():
    from controllers import auth
    from controllers import cloudant_store

    global __api_impl
    with __api_impl_lock:
        if __api_impl is None:
            __api_impl = API(
                auth.GrafeasAuthClient(),
                cloudant_store.CloudantStore())
        return __api_impl
