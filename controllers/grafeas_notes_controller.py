import connexion
import http
import logging
from controllers import api
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.notes")


def create_note(project_id, body):
    """
    Creates a new &#x60;Note&#x60;.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """

    try:
        api_impl = api.get_api_impl()
        note_id = body['id']
        doc = api_impl.write_note(connexion.request, project_id, note_id, body, mode='create')
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while creating a note")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while creating a note")
        return exceptions.InternalServerError(str(e)).to_error()


def update_note(project_id, note_id, body):
    """
    Updates an existing &#x60;Note&#x60;.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str
    :param body:
    :type body: dict | bytes

    :rtype: ApiNote
    """

    try:
        api_impl = api.get_api_impl()
        doc = api_impl.write_note(connexion.request, project_id, note_id, body, mode='update')
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while updating a note")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while updating a note")
        return exceptions.InternalServerError(str(e)).to_error()


def list_notes(project_id, account_id=None, filter=None, page_size=None, page_token=None):
    """
    Lists all &#x60;Notes&#x60; for a given project.

    :param project_id: Part of &#x60;parent&#x60;. This field contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param account_id: Account ID of requested notes if different from subject's account ID
    :type account_id: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNotesResponse
    """

    try:
        api_impl = api.get_api_impl()
        docs = api_impl.list_notes(connexion.request, project_id, account_id, filter, page_size, page_token)
        return common.build_result(http.HTTPStatus.OK, docs)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing notes")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while listing notes")
        return exceptions.InternalServerError(str(e)).to_error()


def get_occurrence_note(project_id, occurrence_id, account_id=None):
    """
    Gets the &#x60;Note&#x60; attached to the given &#x60;Occurrence&#x60;.

    :param project_id: First part of occurrence &#x60;name&#x60;: projects/{project_id}/occurrences/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: projects/{project_id}/occurrences/{occurrence_id}
    :type occurrence_id: str
    :param account_id: Account ID of requested note if different from subject's account ID
    :type account_id: str

    :rtype: ApiNote
    """

    try:
        api_impl = api.get_api_impl()
        docs = api_impl.get_occurrence_note(connexion.request, project_id, occurrence_id, account_id)
        return common.build_result(http.HTTPStatus.OK, docs)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while getting an occurrence's note")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while getting an occurrence's note")
        return exceptions.InternalServerError(str(e)).to_error()


def get_note(project_id, note_id, account_id=None):
    """
    Returns the requested &#x60;Note&#x60;.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str
    :param account_id: Account ID of requested note if different from subject's account ID
    :type account_id: str

    :rtype: ApiNote
    """

    try:
        api_impl = api.get_api_impl()
        doc = api_impl.get_note(connexion.request, project_id, note_id, account_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while getting a note")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while getting a note")
        return exceptions.InternalServerError(str(e)).to_error()


def delete_note(project_id, note_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str

    :rtype: ApiEmpty
    """

    try:
        api_impl = api.get_api_impl()
        api_impl.delete_note(connexion.request, project_id, note_id)
        return common.build_result(http.HTTPStatus.OK, {})
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting a note")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while deleting a note")
        return exceptions.InternalServerError(str(e)).to_error()

