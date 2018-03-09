import connexion
import datetime
from http import HTTPStatus
import isodate
import logging
from . import common
from util import auth_util
from util import exceptions


logger = logging.getLogger("grafeas.notes")


def create_note(project_id, body):
    """
    Creates a new &#x60;Note&#x60;.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_write_note(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to create notes: {}".format(subject))
    except Exception as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, str(e))

    project_doc_id = common.build_project_doc_id(subject.account_id, project_id)

    if 'id' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Missing required field: 'id'")

    note_id = body['id']
    note_name = common.build_note_name(project_id, note_id)

    if 'kind' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Missing required field: 'kind'")

    kind = body['kind']

    if kind not in ['CARD', 'FINDING', 'KPI', 'CARD_CONFIGURED']:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Invalid 'kind' value, only 'CARD', 'CARD_CONFIGURED', 'FINDING', and 'KPI' are allowed")

    if kind == 'FINDING' and 'finding' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Missing field for 'FINDING' note: 'finding")
    if kind == 'KPI' and 'kpi' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Missing field for 'KPI' note: 'kpi'")

    body['doc_type'] = 'Note'
    body['id'] = note_id
    body['account_id'] = subject.account_id
    body['project_id'] = project_id
    body['name'] = note_name
    body['project_doc_id'] = project_doc_id

    if 'create_time' in body:
        create_datetime = isodate.parse_datetime(body['create_time'])
        create_timestamp = create_datetime.timestamp()
    else:
        create_datetime = datetime.datetime.utcnow()
        create_timestamp = create_datetime.timestamp()
        body['create_time'] = create_datetime.isoformat() + 'Z'
    body['update_time'] = body['create_time']
    body['create_timestamp'] = create_timestamp
    body['update_timestamp'] = create_timestamp
    body['update_week_date'] = _week_date_iso_format(create_datetime.isocalendar())

    if 'shared' not in body:
        body['shared'] = True

    try:
        note_doc_id = common.build_note_doc_id(subject.account_id, project_id, note_id)
        db.create_doc(note_doc_id, body)
        return common.build_result(HTTPStatus.OK, _clean_doc(body))
    except exceptions.AlreadyExistsError:
        return common.build_error(HTTPStatus.CONFLICT, "Note already exists: {}".format(note_doc_id))


def update_note(project_id, note_id, body):
    """
    Updates an existing &#x60;Note&#x60;.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str
    :param body:
    :type body: dict | bytes

    :rtype: ApiNote
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_write_note(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to update notes: {}".format(subject))
    except Exception as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, str(e))

    body['id'] = note_id

    if 'update_time' in body:
        update_datetime = isodate.parse_datetime(body['update_time'])
        update_timestamp = update_datetime.timestamp()
    else:
        update_datetime = datetime.datetime.utcnow()
        update_timestamp = update_datetime.timestamp()
        body['update_time'] = update_datetime.isoformat() + 'Z'
    body['update_timestamp'] = update_timestamp
    body['update_week_date'] = _week_date_iso_format(update_datetime.isocalendar())

    try:
        note_doc_id = common.build_note_doc_id(subject.account_id, project_id, note_id)
        doc = db.update_doc(note_doc_id, body)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_doc_id))


def list_notes(project_id, filter=None, page_size=None, page_token=None):
    """
    Lists all &#x60;Notes&#x60; for a given project.

    :param Account: The unique ID of your cloud account.
    :type Account: str
    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNotesResponse
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_read_note(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to list notes: {}".format(subject))
    except Exception as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, str(e))

    project_doc_id = common.build_project_doc_id(subject.account_id, project_id)

    docs = db.find(
        filter_={
            'doc_type': 'Note',
            'project_doc_id': project_doc_id
        },
        index="DT_PDI_TS")
    return common.build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def get_note(project_id, note_id):
    """
    Returns the requested &#x60;Note&#x60;.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str

    :rtype: ApiNote
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_read_note(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to get notes: {}".format(subject))
    except Exception as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, str(e))

    try:
        note_doc_id = common.build_note_doc_id(subject.account_id, project_id, note_id)
        doc = db.get_doc(note_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_doc_id))


def get_occurrence_note(project_id, occurrence_id):
    """
    Gets the &#x60;Note&#x60; attached to the given &#x60;Occurrence&#x60;.

    :param Account: The unique ID of your cloud account.
    :type Account: str
    :param project_id: First part of occurrence &#x60;name&#x60;: projects/{project_id}/occurrences/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: projects/{project_id}/occurrences/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiNote
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_read_note(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to get occurrence notes: {}".format(subject))
    except Exception as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, str(e))

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(subject.account_id, project_id, occurrence_id)
        occurrence_doc = db.get_doc(occurrence_doc_id)
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_doc_id))

    try:
        note_name = occurrence_doc['note_name']
        note_doc_id = "{}/{}".format(subject.account_id, note_name)
        doc = db.get_doc(note_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_doc_id))


def delete_note(project_id, note_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str

    :rtype: ApiEmpty
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_delete_note(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to delete notes: {}".format(subject))
    except Exception as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, str(e))

    try:
        note_doc_id = common.build_note_doc_id(subject.account_id, project_id, note_id)
        doc = db.delete_doc(note_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_doc_id))


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    doc.pop('account_id', None)
    return doc


def _week_date_iso_format(iso_calendar):
    return "{:04d}-W{:02d}-{}".format(iso_calendar[0], iso_calendar[1], iso_calendar[2])
