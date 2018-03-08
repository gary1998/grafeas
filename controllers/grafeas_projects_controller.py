import connexion
from http import HTTPStatus
from . import common
from util import auth_util
from util import exceptions


def create_project(body):
    """
    Creates a new &#x60;Project&#x60;.

    :param body:
    :type body: dict | bytes

    :rtype: ApiEmpty
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_write_project(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to create projects: {}".format(subject))
    except ValueError as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, e)

    if 'id' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Project's 'project_id' field is missing")

    project_id = body['id']
    body['doc_type'] = 'Project'
    body['account_id'] = subject.account_id
    body['id'] = project_id
    body['name'] = common.build_project_name(project_id)

    if 'shared' not in body:
        body['shared'] = True

    try:
        project_doc_id = common.build_project_doc_id(subject.account_id, project_id)
        db.create_doc(project_doc_id, body)
        return common.build_result(HTTPStatus.OK, _clean_doc(body))
    except exceptions.AlreadyExistsError:
        return common.build_error(HTTPStatus.CONFLICT, "Project already exists: {}".format(project_id))


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

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_read_project(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to list projects: {}".format(subject))
    except ValueError as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, e)

    docs = db.find(
        filter_={
            'doc_type': 'Project',
            'account_id': subject.account_id
        },
        index="DT_OAI_TS")
    return common.build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def get_project(project_id):
    """
    Returns the requested &#x60;Project&#x60;.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str

    :rtype: ApiProject
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_read_project(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to get projects: {}".format(subject))
    except ValueError as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, e)

    try:
        project_doc_id = common.build_project_doc_id(subject.account_id, project_id)
        doc = db.get_doc(project_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Project not found: {}".format(project_id))


def delete_project(project_id):
    """
    Deletes the given &#x60;Project&#x60; from the system.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str

    :rtype: ApiEmpty
    """

    db = common.get_db()
    auth_client = common.get_auth_client()

    try:
        subject = auth_util.get_subject(connexion.request)
        if not auth_client.can_delete_project(subject):
            return common.build_error(HTTPStatus.FORBIDDEN, "Not allowed to delete projects: {}".format(subject))
    except ValueError as e:
        return common.build_error(HTTPStatus.UNAUTHORIZED, e)

    try:
        project_doc_id = common.build_project_doc_id(subject.account_id, project_id)
        doc = db.delete_doc(project_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Project not found: {}".format(project_id))


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    doc.pop('account_id', None)
    return doc
