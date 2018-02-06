import connexion
from http import HTTPStatus
from .common import get_store
from .common import build_project_doc_id, build_project_name
from .common import build_result, build_error


def create_project(body):
    """
    Creates a new &#x60;Project&#x60;.

    :param body:
    :type body: dict | bytes

    :rtype: ApiEmpty
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    if 'id' not in body:
        return build_error(HTTPStatus.BAD_REQUEST, "Project's 'project_id' field is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    project_id = body['id']
    project_doc_id = build_project_doc_id(account_id, project_id)
    body['doc_type'] = 'Project'
    body['account_id'] = account_id
    body['id'] = project_id
    body['name'] = build_project_name(project_id)

    try:
        store.create_doc(project_doc_id, body)
        return build_result(HTTPStatus.OK, _clean_doc(body))
    except KeyError:
        return build_error(HTTPStatus.CONFLICT, "Project already exists: {}".format(project_doc_id))


def delete_project(project_id):
    """
    Deletes the given &#x60;Project&#x60; from the system.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str

    :rtype: ApiEmpty
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    project_doc_id = build_project_doc_id(account_id, project_id)

    try:
        doc = store.delete_doc(project_doc_id)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Project not found: {}".format(project_doc_id))


def get_project(project_id):
    """
    Returns the requested &#x60;Project&#x60;.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str

    :rtype: ApiProject
    """

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    project_doc_id = build_project_doc_id(account_id, project_id)

    try:
        doc = store.get_doc(project_doc_id)
        return build_result(HTTPStatus.OK, _clean_doc(doc))
    except KeyError:
        return build_error(HTTPStatus.NOT_FOUND, "Project not found: {}".format(project_doc_id))


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

    if 'Account' not in connexion.request.headers:
        return build_error(HTTPStatus.BAD_REQUEST, "'Account' header is missing")

    store = get_store()
    account_id = connexion.request.headers['Account']
    docs = store.find(
        filter_={
            'doc_type': 'Project',
            'account_id': account_id
        },
        index="DT_AI")
    return build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    doc.pop('account_id', None)
    return doc