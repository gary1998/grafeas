import connexion
from http import HTTPStatus
import logging
from . import common
from util import auth_util
from util import exceptions


logger = logging.getLogger("grafeas.projects")


def create_project(body):
    """
    Creates a new &#x60;Project&#x60;.

    :param body:
    :type body: dict | bytes

    :rtype: ApiEmpty
    """

    try:
        db = common.get_db()
        auth_client = common.get_auth_client()

        try:
            subject = auth_util.get_subject(connexion.request)
            if not auth_client.can_write_project(subject):
                return common.build_error(
                    HTTPStatus.FORBIDDEN,
                    "Not allowed to create projects: {}".format(subject),
                    logger)
        except Exception as e:
            return common.build_error(HTTPStatus.UNAUTHORIZED, str(e), logger)

        if 'id' not in body:
            return common.build_error(
                HTTPStatus.BAD_REQUEST,
                "Missing required field: project_id",
                logger)

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
            return common.build_error(
                HTTPStatus.CONFLICT,
                "Project already exists: {}".format(project_doc_id),
                logger)
    except:
        logger.exception("An unexpected error was encountered while creating a project")
        raise


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

    try:
        db = common.get_db()
        auth_client = common.get_auth_client()

        try:
            subject = auth_util.get_subject(connexion.request)
            if not auth_client.can_read_project(subject):
                return common.build_error(
                    HTTPStatus.FORBIDDEN,
                    "Not allowed to list projects: {}".format(subject),
                    logger)
        except Exception as e:
            return common.build_error(HTTPStatus.UNAUTHORIZED, str(e), logger)

        docs = db.find(
            filter_={
                'account_id': subject.account_id,
                'doc_type': 'Project'
            },
            index="SAI_DT")
        return common.build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])
    except:
        logger.exception("An unexpected error was encountered while listing projects")
        raise


def get_project(project_id):
    """
    Returns the requested &#x60;Project&#x60;.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str

    :rtype: ApiProject
    """

    try:
        db = common.get_db()
        auth_client = common.get_auth_client()

        try:
            subject = auth_util.get_subject(connexion.request)
            if not auth_client.can_read_project(subject):
                return common.build_error(
                    HTTPStatus.FORBIDDEN,
                    "Not allowed to get projects: {}".format(subject),
                    logger)
        except Exception as e:
            return common.build_error(HTTPStatus.UNAUTHORIZED, str(e), logger)

        try:
            project_doc_id = common.build_project_doc_id(subject.account_id, project_id)
            doc = db.get_doc(project_doc_id)
            return common.build_result(HTTPStatus.OK, _clean_doc(doc))
        except exceptions.NotFoundError:
            return common.build_error(
                HTTPStatus.NOT_FOUND,
                "Project not found: {}".format(project_doc_id),
                logger)
    except:
        logger.exception("An unexpected error was encountered while getting a project")
        raise


def delete_project(project_id):
    """
    Deletes the given &#x60;Project&#x60; from the system.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str

    :rtype: ApiEmpty
    """

    try:
        db = common.get_db()
        auth_client = common.get_auth_client()

        try:
            subject = auth_util.get_subject(connexion.request)
            if not auth_client.can_delete_project(subject):
                return common.build_error(
                    HTTPStatus.FORBIDDEN,
                    "Not allowed to delete projects: {}".format(subject),
                    logger)
        except Exception as e:
            return common.build_error(HTTPStatus.UNAUTHORIZED, str(e), logger)

        try:
            project_doc_id = common.build_project_doc_id(subject.account_id, project_id)
            doc = db.delete_doc(project_doc_id)
            return common.build_result(HTTPStatus.OK, _clean_doc(doc))
        except exceptions.NotFoundError:
            return common.build_error(
                HTTPStatus.NOT_FOUND,
                "Project not found: {}".format(project_doc_id),
                logger)
    except:
        logger.exception("An unexpected error was encountered while deleting a project")
        raise


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    doc.pop('account_id', None)
    return doc
