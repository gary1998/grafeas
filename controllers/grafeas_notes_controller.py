import connexion
from http import HTTPStatus
from .common import get_store
from .common import build_project_doc_id, build_note_doc_id, build_occurrence_doc_id
from .common import build_result, build_error


def create_note(project_id, body):
    """
    Creates a new &#x60;Note&#x60;.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    if 'name' not in body:
        return build_error(HTTPStatus.BAD_REQUEST, "Note 'name' is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    note_doc_id = "{}/{}".format(account_id, body['name'])
    project_doc_id = build_project_doc_id(account_id, project_id)
    body['doc_type'] = 'Note'
    body['account_id'] = account_id
    body['project_doc_id'] = project_doc_id

    try:
        store.create_doc(note_doc_id, body)
        return build_result(HTTPStatus.OK, _clean_doc(body))
    except KeyError:
        return build_error(HTTPStatus.CONFLICT, "Note already exists")


def delete_note(project_id, note_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str

    :rtype: ApiEmpty
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    note_doc_id = build_note_doc_id(account_id, project_id, note_id)

    try:
        doc = store.delete_doc(note_doc_id)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_doc_id))


def get_note(project_id, note_id):
    """
    Returns the requested &#x60;Note&#x60;.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str

    :rtype: ApiNote
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    note_doc_id = build_note_doc_id(account_id, project_id, note_id)

    try:
        doc = store.get_doc(note_doc_id)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_doc_id))


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
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    occurrence_doc_id = build_occurrence_doc_id(account_id, project_id, occurrence_id)

    try:
        occurrence_doc = store.get_doc(occurrence_doc_id)

        try:
            note_name = occurrence_doc['noteName']
            note_doc_id = "{}/{}".format(account_id, note_name)
            doc = store.get_doc(note_doc_id)
            return build_result(HTTPStatus.OK, _clean_doc(doc))
        except KeyError:
            return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_doc_id))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_doc_id))


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

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    project_doc_id = build_project_doc_id(account_id, project_id)
    docs = store.find(
        filter_={
            'doc_type': 'Note',
            'project_doc_id': project_doc_id
        },
        index="DT_PDI")
    return build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


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

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    note_doc_id = build_note_doc_id(account_id, project_id, note_id)

    try:
        doc = store.update_doc(note_doc_id, body)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(note_doc_id))


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    return doc
