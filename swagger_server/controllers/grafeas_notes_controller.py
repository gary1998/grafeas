import connexion
from http import HTTPStatus
from swagger_server.controllers.common import get_store
from swagger_server.controllers.common import build_result, build_error


def create_note(projectId, body):
    """
    Creates a new &#x60;Note&#x60;.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """

    if 'name' not in body:
        return build_error(HTTPStatus.BAD_REQUEST, "Note name is missing")

    store = get_store()
    name = body['name']
    parent = "projects/{}".format(projectId)
    body['doc_type'] = 'Note'
    body['parent'] = parent

    try:
        store.create_doc(name, body)
        return build_result(HTTPStatus.OK, _clean_doc(body))
    except KeyError:
        return build_error(HTTPStatus.CONFLICT, "Note already exists")


def delete_note(projectId, noteId):
    """
    Deletes the given &#x60;Note&#x60; from the system.
    
    :param projectId: First part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type projectId: str
    :param noteId: Second part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type noteId: str

    :rtype: ApiEmpty
    """

    store = get_store()
    name = "projects/{}/notes/{}".format(projectId, noteId)

    try:
        doc = store.delete_doc(name)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(name))


def get_note(projectId, noteId):
    """
    Returns the requested &#x60;Note&#x60;.
    
    :param projectId: First part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type projectId: str
    :param noteId: Second part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type noteId: str

    :rtype: ApiNote
    """

    store = get_store()
    name = "projects/{}/notes/{}".format(projectId, noteId)

    try:
        doc = store.get_doc(name)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(name))


def get_occurrence_note(projectId, occurrenceId):
    """
    Gets the &#x60;Note&#x60; attached to the given &#x60;Occurrence&#x60;.
    
    :param projectId: First part of occurrence &#x60;name&#x60;: projects/{projectId}/occurrences/{occurrenceId}
    :type projectId: str
    :param occurrenceId: Second part of occurrence &#x60;name&#x60;: projects/{projectId}/occurrences/{occurrenceId}
    :type occurrenceId: str

    :rtype: ApiNote
    """

    store = get_store()
    occurrence_name = "projects/{}/occurreces/{}".format(projectId, occurrenceId)

    try:
        occurrence_doc = store.get_doc(occurrence_name)

        try:
            name = occurrence_doc['noteName']
            doc = store.get_doc(name)
            return build_result(HTTPStatus.OK, _clean_doc(doc))
        except KeyError:
            return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(name))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_name))


def list_notes(projectId, filter=None, page_size=None, page_token=None):
    """
    Lists all &#x60;Notes&#x60; for a given project.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNotesResponse
    """

    store = get_store()
    parent = "projects/{}".format(projectId)
    docs = store.find(
        filter_={
            'doc_type': 'Note',
            'parent': parent
        },
        index="DT_P")
    return build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def update_note(projectId, noteId, body):
    """
    Updates an existing &#x60;Note&#x60;.
    
    :param projectId: First part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type projectId: str
    :param noteId: Second part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type noteId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """

    store = get_store()
    name = "projects/{}/notes/{}".format(projectId, noteId)

    try:
        doc = store.update_doc(name, body)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Note not found: {}".format(name))


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    return doc
