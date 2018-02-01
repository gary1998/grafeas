import connexion
from http import HTTPStatus
from swagger_server.controllers.common import get_store
from swagger_server.controllers.common import build_result, build_error


def create_project(body):
    """
    Creates a new &#x60;Project&#x60;.
    
    :param body: 
    :type body: dict | bytes

    :rtype: ApiEmpty
    """

    if 'name' not in body:
        return build_error(HTTPStatus.BAD_REQUEST, "Project name is missing")

    store = get_store()
    name = body['name']
    body['doc_type'] = 'Project'

    try:
        store.create_doc(name, body)
        return build_result(HTTPStatus.OK, _clean_doc(body))
    except KeyError:
        return build_error(HTTPStatus.CONFLICT, "Project already exists")


def delete_project(projectId):
    """
    Deletes the given &#x60;Project&#x60; from the system.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str

    :rtype: ApiEmpty
    """

    store = get_store()
    name = "projects/{}".format(projectId)

    try:
        doc = store.delete_doc(name)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Project not found: {}".format(name))


def get_project(projectId):
    """
    Returns the requested &#x60;Project&#x60;.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str

    :rtype: ApiProject
    """

    store = get_store()
    name = "projects/{}".format(projectId)

    try:
        doc = store.get_doc(name)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Project not found: {}".format(name))


def list_projects(filter=None, page_size=None, page_token=None):
    """
    Lists &#x60;Projects&#x60;
    
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of projects to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListProjectsResponse
    """

    store = get_store()
    docs = store.find(
        filter_={'doc_type': 'Project'},
        index="DT_N")
    return build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def update_project(projectId, body):
    """
    Updates an existing &#x60;Project&#x60;.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiProject
    """

    store = get_store()
    name = "projects/{}".format(projectId)
    try:
        doc = store.update_doc(name, body)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Project not found: {}".format(name))


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    return doc