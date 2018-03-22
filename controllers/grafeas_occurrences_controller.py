import connexion
import http
import logging
from controllers import api
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
        api_impl = api.get_api_impl()

        replace_if_exists_header = connexion.request.headers.get('Replace-If-Exists')
        if replace_if_exists_header is not None and replace_if_exists_header.lower() == 'true':
            mode = 'replace'
        else:
            mode = 'create'

        doc = api_impl.write_occurrence(connexion.request, project_id, body['id'], body, mode)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while creating an occurrence")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while creating an occurrence")
        raise


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
        api_impl = api.get_api_impl()
        doc = api_impl.write_occurrence(connexion.request, project_id,  occurrence_id, body, mode='update')
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while updating an occurrence")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while updating a occurrence")
        raise


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
        api_impl = api.get_api_impl()
        docs = api_impl.list_occurrences(connexion.request, project_id, filter, page_size, page_token)
        return common.build_result(http.HTTPStatus.OK, docs)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing occurrences")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while listing occurrences")
        raise


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
        api_impl = api.get_api_impl()
        docs = api_impl.list_note_occurrences(connexion.request, project_id, note_id, filter, page_size, page_token)
        return common.build_result(http.HTTPStatus.OK, docs)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing note occurrences")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while listing note occurrences")
        raise


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
        api_impl = api.get_api_impl()
        doc = api_impl.get_occurrence(connexion.request, project_id, occurrence_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while getting an occurrence")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while getting an occurrence")
        raise


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
        api_impl = api.get_api_impl()
        doc = api_impl.delete_occurrence(connexion.request, project_id, occurrence_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting an occurrence")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while deleting an occurrence")
        raise
