import connexion
import datetime
from http import HTTPStatus
import isodate
from . import common


def create_note(project_id, body):
    """
    Creates a new &#x60;Note&#x60;.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """

    if 'Account' in connexion.request.headers:
        account_id = connexion.request.headers['Account']
    else:
        account_id = common.SHARED_ACCOUNT_ID

    if 'id' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Field 'id' is missing")

    if 'create_time' in body:
        create_timestamp = isodate.parse_datetime(body['create_time']).timestamp()
    else:
        now = datetime.datetime.now()
        create_timestamp = now.timestamp()
        body['create_time'] = isodate.datetime_isoformat(now)
    body['update_time'] = body['create_time']

    store = common.get_store()

    note_id = body['id']
    note_name = common.build_note_name(project_id, note_id)

    project_doc_id = common.build_project_doc_id(account_id, project_id)
    body['doc_type'] = 'Note'
    body['account_id'] = account_id
    body['project_id'] = project_id
    body['id'] = note_id
    body['name'] = note_name
    body['project_doc_id'] = project_doc_id
    body['create_timestamp'] = create_timestamp
    body['update_timestamp'] = create_timestamp

    try:
        note_doc_id = common.build_note_doc_id(account_id, project_id, note_id)
        store.create_doc(note_doc_id, body)
        return common.build_result(HTTPStatus.OK, _clean_doc(body))
    except KeyError:
        return common.build_error(HTTPStatus.CONFLICT, "Note already exists: {}".format(note_name))


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

    if 'Account' in connexion.request.headers:
        account_id = connexion.request.headers['Account']
    else:
        account_id = common.SHARED_ACCOUNT_ID

    private_project_doc_id = common.build_project_doc_id(account_id, project_id)
    shared_project_doc_id = common.build_project_doc_id(common.SHARED_ACCOUNT_ID, project_id)
    if account_id == common.SHARED_ACCOUNT_ID:
        project_doc_id_filter = shared_project_doc_id
    else:
        project_doc_id_filter = [
            private_project_doc_id,
            shared_project_doc_id
        ]

    store = common.get_store()

    docs = store.find(
        filter_={
            'doc_type': 'Note',
            'project_doc_id': project_doc_id_filter
        },
        index="DT_PDI")
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

    if 'Account' in connexion.request.headers:
        account_id = connexion.request.headers['Account']
    else:
        account_id = common.SHARED_ACCOUNT_ID

    store = common.get_store()

    try:
        note_doc_id = common.build_note_doc_id(account_id, project_id, note_id)
        doc = store.get_doc(note_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        try:
            note_doc_id = common.build_note_doc_id(common.SHARED_ACCOUNT_ID, project_id, note_id)
            doc = store.get_doc(note_doc_id)
            return common.build_result(HTTPStatus.OK, _clean_doc(doc))
        except KeyError:
            note_name = common.build_note_name(project_id, note_id)
            return common.build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_name))


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

    if 'Account' in connexion.request.headers:
        account_id = connexion.request.headers['Account']
    else:
        account_id = common.SHARED_ACCOUNT_ID

    if 'update_time' in body:
        update_timestamp = isodate.parse_datetime(body['update_time']).timestamp()
    else:
        now = datetime.datetime.now()
        update_timestamp = now.timestamp()
        body['update_time'] = isodate.datetime_isoformat(now)

    store = common.get_store()
    body['id'] = note_id
    body['update_timestamp'] = update_timestamp

    try:
        note_doc_id = common.build_note_doc_id(account_id, project_id, note_id)
        doc = store.update_doc(note_doc_id, body)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        note_name = common.build_note_name(project_id, note_id)
        return common.build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_name))


def delete_note(project_id, note_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str

    :rtype: ApiEmpty
    """

    if 'Account' in connexion.request.headers:
        account_id = connexion.request.headers['Account']
    else:
        account_id = common.SHARED_ACCOUNT_ID

    store = common.get_store()

    try:
        note_doc_id = common.build_note_doc_id(account_id, project_id, note_id)
        doc = store.delete_doc(note_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        note_name = common.build_note_name(project_id, note_id)
        return common.build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_name))


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

    if 'Account' not in connexion.request.headers:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Header 'Account' is missing")

    store = common.get_store()
    account_id = connexion.request.headers['Account']
    occurrence_doc_id = common.build_occurrence_doc_id(account_id, project_id, occurrence_id)

    try:
        occurrence_doc = store.get_doc(occurrence_doc_id)

        try:
            note_name = occurrence_doc['note_name']
            note_doc_id = "{}/{}".format(account_id, note_name)
            doc = store.get_doc(note_doc_id)
            return common.build_result(HTTPStatus.OK, _clean_doc(doc))
        except KeyError:
            return common.build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_name))
    except KeyError:
        occurrence_name = common.build_occurrence_name(project_id, occurrence_id)
        return common.build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_name))


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    doc.pop('account_id', None)
    return doc
