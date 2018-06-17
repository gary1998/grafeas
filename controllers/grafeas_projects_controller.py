import connexion
import http
import logging
from controllers import api
from controllers import auth
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.projects")


def create_project(account_id, body):
    """
    Creates a new &#x60;Project&#x60;.

    :param body:
    :type body: dict | bytes

    :rtype: ApiEmpty
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_write_projects(connexion.request, account_id)

        api_impl = api.get_api_impl()
        doc = api_impl.create_project(subject.account_id, account_id, body)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while creating a project")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while creating a project")
        return exceptions.InternalServerError(str(e)).to_error()


def list_projects(account_id, filter=None, page_size=None, page_token=None):
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
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_projects(connexion.request, account_id)

        api_impl = api.get_api_impl()
        result = api_impl.list_projects(subject.account_id, account_id, filter, page_size, page_token)
        return common.build_result(
            http.HTTPStatus.OK,
            {
                "projects": result.docs,
                "next_page_token": result.bookmark
            })
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing projects")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while listing projects")
        return exceptions.InternalServerError(str(e)).to_error()


def get_project(account_id, project_id):
    """
    Returns the requested &#x60;Project&#x60;.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str

    :rtype: ApiProject
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_projects(connexion.request, account_id)

        api_impl = api.get_api_impl()
        doc = api_impl.get_project(subject.account_id, account_id, project_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while getting a project")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while getting a project")
        return exceptions.InternalServerError(str(e)).to_error()


def delete_project(account_id, project_id):
    """
    Deletes the given &#x60;Project&#x60; from the system.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str

    :rtype: ApiEmpty
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_delete_projects(connexion.request, account_id)

        api_impl = api.get_api_impl()
        doc = api_impl.delete_project(subject.account_id, account_id, project_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting a project")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while deleting a project")
        return exceptions.InternalServerError(str(e)).to_error()
