import connexion
import http
import logging
from controllers import api
from controllers import auth
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.occurrences")


def create_occurrence(project_id, body):
    """
    Creates a new &#x60;Occurrence&#x60;. Use this method to create &#x60;Occurrences&#x60; for a resource.

    :param project_id: Part of &#x60;parent&#x60;. This contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiOccurrence
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.get_subject(connexion.request)
        auth_client.assert_can_write_occurrences(subject)

        # context.account_id is required in swagger's `Occurrence` definition
        resource = body['context']
        resource_account_id = resource['account_id']
        if resource_account_id != subject.account_id:
            auth_client.assert_can_write_occurrences_for_others(subject)

        replace_if_exists = connexion.request.headers.get('Replace-If-Exists', 'false').lower()
        mode = 'replace' if replace_if_exists == 'true' else 'create'

        api_impl = api.get_api_impl()
        occurrence_id = body['id']
        doc = api_impl.write_occurrence(subject.account_id, project_id, occurrence_id, body, mode)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while creating an occurrence")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while creating an occurrence")
        return exceptions.InternalServerError(str(e)).to_error()


def update_occurrence(project_id, occurrence_id, body):
    """
    Updates an existing &#x60;Note&#x60;.

    :param project_id: First part of occurrence &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type occurrence_id: str
    :param body:
    :type body: dict | bytes

    :rtype: ApiNote
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.get_subject(connexion.request)
        auth_client.assert_can_write_occurrences(subject)

        # context.account_id is required in swagger's `Occurrence` definition
        resource = body['context']
        resource_account_id = resource['account_id']
        if resource_account_id != subject.account_id:
            auth_client.assert_can_write_occurrences_for_others(subject)

        api_impl = api.get_api_impl()
        doc = api_impl.write_occurrence(subject.account_id, project_id, occurrence_id, body, mode='update')
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while updating an occurrence")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while updating a occurrence")
        return exceptions.InternalServerError(str(e)).to_error()


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

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.get_subject(connexion.request)
        auth_client.assert_can_read_occurrences(subject)

        api_impl = api.get_api_impl()
        docs = api_impl.list_occurrences(subject.account_id, project_id, filter, page_size, page_token)
        return common.build_result(http.HTTPStatus.OK, docs)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing occurrences")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while listing occurrences")
        return exceptions.InternalServerError(str(e)).to_error()


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

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.get_subject(connexion.request)
        auth_client.assert_can_read_occurrences(subject)

        api_impl = api.get_api_impl()
        docs = api_impl.list_note_occurrences(subject.account_id, project_id, note_id, filter, page_size, page_token)
        return common.build_result(http.HTTPStatus.OK, docs)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing note occurrences")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while listing note occurrences")
        return exceptions.InternalServerError(str(e)).to_error()


def get_occurrence(project_id, occurrence_id):
    """
    Returns the requested &#x60;Note&#x60;.

    :param project_id: First part of occurrence &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiOccurrence
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.get_subject(connexion.request)
        auth_client.assert_can_read_occurrences(subject)

        api_impl = api.get_api_impl()
        doc = api_impl.get_occurrence(subject.account_id, project_id, occurrence_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while getting an occurrence")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while getting an occurrence")
        return exceptions.InternalServerError(str(e)).to_error()


def delete_occurrence(project_id, occurrence_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param project_id: First part of occurrence &#x60;name&#x60;: projects/{project_id}/occurrences/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: projects/{project_id}/occurrences/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiEmpty
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.get_subject(connexion.request)
        auth_client.assert_can_delete_occurrences(subject)

        api_impl = api.get_api_impl()
        doc = api_impl.delete_occurrence(subject.account_id, project_id, occurrence_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting an occurrence")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while deleting an occurrence")
        return exceptions.InternalServerError(str(e)).to_error()
