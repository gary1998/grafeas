import connexion
from http import HTTPStatus
from .common import get_store
from .common import build_project_doc_id, build_note_doc_id, build_occurrence_doc_id, build_occurrence_name
from .common import build_result, build_error


def create_occurrence(project_id, body):
    """
    Creates a new &#x60;Occurrence&#x60;. Use this method to create &#x60;Occurrences&#x60; for a resource.

    :param project_id: Part of &#x60;parent&#x60;. This contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiOccurrence
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "Header 'Account' is missing")

    if 'id' not in body:
        return build_error(HTTPStatus.BAD_REQUEST, "Field 'id' is missing")

    if 'noteName' not in body:
        return build_error(HTTPStatus.BAD_REQUEST, "Field 'noteName' is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    occurrence_id = body['id']
    occurrence_doc_id = build_occurrence_doc_id(account_id, project_id, occurrence_id)
    project_doc_id = build_project_doc_id(account_id, project_id)
    note_doc_id = "{}/{}".format(account_id, body['noteName'])
    body['doc_type'] = 'Occurrence'
    body['account_id'] = account_id
    body['project_id'] = project_id
    body['id'] = occurrence_id
    body['name'] = build_occurrence_name(project_id, occurrence_id)
    body['project_doc_id'] = project_doc_id
    body['note_doc_id'] = note_doc_id

    # merge occurrence values with note values
    try:
        note = store.get_doc(note_doc_id)
        try:
            doc = _dict_merge(note, body)
            store.create_doc(occurrence_doc_id, doc)
            return build_result(HTTPStatus.OK, _clean_doc(doc))
        except KeyError:
            return build_error(HTTPStatus.CONFLICT, "Occurrence already exists: {}".format(occurrence_doc_id))
    except KeyError:
        return build_error(HTTPStatus.BAD_REQUEST, "Specified note not found")


def get_occurrence(project_id, occurrence_id):
    """
    Returns the requested &#x60;Note&#x60;.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiOccurrence
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "Header 'Account' is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    occurrence_doc_id = build_occurrence_doc_id(account_id, project_id, occurrence_id)

    try:
        doc = store.get_doc(occurrence_doc_id)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(occurrence_doc_id))


def delete_occurrence(project_id, occurrence_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiEmpty
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "Header 'Account' is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    occurrence_doc_id = build_occurrence_doc_id(account_id, project_id, occurrence_id)

    try:
        doc = store.delete_doc(occurrence_doc_id)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(occurrence_doc_id))


def list_note_occurrences(project_id, note_id, filter=None, page_size=None, page_token=None):
    """
    Lists &#x60;Occurrences&#x60; referencing the specified &#x60;Note&#x60;.
    Use this method to get all occurrences referencing your &#x60;Note&#x60; across all your customer projects.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNoteOccurrencesResponse
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "Header 'Account' is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    note_doc_id = build_note_doc_id(account_id, project_id, note_id)
    docs = store.find(
        filter_={
            'doc_type': 'Occurrence',
            'note_doc_id': note_doc_id
        },
        index="DT_NDI")
    return build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def list_occurrences(project_id, filter=None, page_size=None, page_token=None):
    """
    Lists active &#x60;Occurrences&#x60; for a given project matching the filters.

    :param project_id: Part of &#x60;parent&#x60;. This contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of occurrences to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListOccurrencesResponse
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "Header 'Account' is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    project_doc_id = build_project_doc_id(account_id, project_id)
    docs = store.find(
        filter_={
            'doc_type': 'Occurrence',
            'project_doc_id': project_doc_id
        },
        index="DT_PDI")
    return build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    doc.pop('account_id', None)
    return doc


def _dict_merge(a, b):
    import copy
    if not isinstance(b, dict):
        return b
    result = copy.deepcopy(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict):
                result[k] = _dict_merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result