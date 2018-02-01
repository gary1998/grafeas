import connexion
from http import HTTPStatus
from swagger_server.controllers.common import get_store
from swagger_server.controllers.common import build_result, build_error


def create_occurrence(projectId, body):
    """
    Creates a new &#x60;Occurrence&#x60;. Use this method to create &#x60;Occurrences&#x60; for a resource.
    
    :param projectId: Part of &#x60;parent&#x60;. This contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiOccurrence
    """

    if 'name' not in body:
        return build_error(HTTPStatus.BAD_REQUEST, "Occurrence name is missing")

    store = get_store()
    name = body['name']
    parent = "projects/{}".format(projectId)
    body['doc_type'] = 'Occurrence'
    body['parent'] = parent

    try:
        store.create_doc(name, body)
        return build_result(HTTPStatus.OK, _clean_doc(body))
    except KeyError:
        return build_error(HTTPStatus.CONFLICT, "Occurrence already exists")


def list_note_occurrences(projectId, noteId, filter=None, page_size=None, page_token=None):
    """
    Lists &#x60;Occurrences&#x60; referencing the specified &#x60;Note&#x60;. Use this method to get all occurrences referencing your &#x60;Note&#x60; across all your customer projects.
    
    :param projectId: First part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type projectId: str
    :param noteId: Second part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type noteId: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNoteOccurrencesResponse
    """

    store = get_store()
    note_name = "projects/{}/notes/{}".format(projectId, )
    docs = store.find(
        filter_={
            'doc_type': 'Occurrence',
            'note_name': note_name
        },
        index="DT_NN")
    return build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def list_occurrences(projectId, filter=None, page_size=None, page_token=None):
    """
    Lists active &#x60;Occurrences&#x60; for a given project matching the filters.
    
    :param projectId: Part of &#x60;parent&#x60;. This contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of occurrences to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListOccurrencesResponse
    """

    store = get_store()
    parent = "projects/{}".format(projectId)
    docs = store.find(
        filter_={
            'doc_type': 'Occurrence',
            'parent': parent
        },
        index="DT_P")
    return build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    return doc

