# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import connexion
import http
import logging
from controllers import api
from controllers import auth
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.notes")

def delete_notes(account_id, provider_id, body):
    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_delete_notes(
            connexion.request, account_id)

        api_impl = api.get_api_impl()
        api_impl.delete_notes(subject, account_id, provider_id, body)
        return common.build_result(http.HTTPStatus.OK, {})
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting notes")
        return e.to_error()
    except Exception as e:
        logger.exception(
            "An unexpected error was encountered while deleting notes")
        return exceptions.InternalServerError(str(e)).to_error()

def create_note(account_id, provider_id, body):
    """
    Creates a new &#x60;Note&#x60;.

    :param provider_id: Part of &#x60;parent&#x60;. This field contains the provider_id for example: providers/{provider_id}
    :type provider_id: str
    :param body:
    :type body: dict | bytes

    :rtype: ApiNote
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_write_notes(
            connexion.request, account_id)

        api_impl = api.get_api_impl()
        note_id = body['id']
        doc = api_impl.write_note(
            subject, account_id, provider_id, note_id, body, mode='create')
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while creating a note")
        return e.to_error()
    except Exception as e:
        logger.exception(
            "An unexpected error was encountered while creating a note")
        return exceptions.InternalServerError(str(e)).to_error()


def update_note(account_id, provider_id, note_id, body):
    """
    Updates an existing &#x60;Note&#x60;.

    :param provider_id: First part of note &#x60;name&#x60;: providers/{provider_id}/notes/{note_id}
    :type provider_id: str
    :param note_id: Second part of note &#x60;name&#x60;: providers/{provider_id}/notes/{note_id}
    :type note_id: str
    :param body:
    :type body: dict | bytes

    :rtype: ApiNote
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_write_notes(
            connexion.request, account_id)

        api_impl = api.get_api_impl()
        doc = api_impl.write_note(
            subject, account_id, provider_id, note_id, body, mode='update')
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while updating a note")
        return e.to_error()
    except Exception as e:
        logger.exception(
            "An unexpected error was encountered while updating a note")
        return exceptions.InternalServerError(str(e)).to_error()


def list_notes(account_id, provider_id, filter=None, page_size=None, page_token=None):
    """
    Lists all &#x60;Notes&#x60; for a given provider.

    :param provider_id: Part of &#x60;parent&#x60;. This field contains the provider_id for example: providers/{provider_id}
    :type provider_id: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNotesResponse
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_notes(
            connexion.request, account_id)

        api_impl = api.get_api_impl()
        result = api_impl.list_notes(
            subject, account_id, provider_id, filter, page_size, page_token)
        return common.build_result(
            http.HTTPStatus.OK,
            {
                "notes": result.docs,
                "next_page_token": result.bookmark
            })
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing notes")
        return e.to_error()
    except Exception as e:
        logger.exception(
            "An unexpected error was encountered while listing notes")
        return exceptions.InternalServerError(str(e)).to_error()


def get_occurrence_note(account_id, provider_id, occurrence_id):
    """
    Gets the &#x60;Note&#x60; attached to the given &#x60;Occurrence&#x60;.

    :param provider_id: First part of occurrence &#x60;name&#x60;: providers/{provider_id}/occurrences/{occurrence_id}
    :type provider_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: providers/{provider_id}/occurrences/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiNote
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_notes(
            connexion.request, account_id)

        api_impl = api.get_api_impl()
        docs = api_impl.get_occurrence_note(
            subject, account_id, provider_id, occurrence_id)
        return common.build_result(http.HTTPStatus.OK, docs)
    except exceptions.JSONError as e:
        logger.exception(
            "An error was encountered while getting an occurrence's note")
        return e.to_error()
    except Exception as e:
        logger.exception(
            "An unexpected error was encountered while getting an occurrence's note")
        return exceptions.InternalServerError(str(e)).to_error()


def get_note(account_id, provider_id, note_id):
    """
    Returns the requested &#x60;Note&#x60;.

    :param provider_id: First part of note &#x60;name&#x60;: providers/{provider_id}/notes/{note_id}
    :type provider_id: str
    :param note_id: Second part of note &#x60;name&#x60;: providers/{provider_id}/notes/{note_id}
    :type note_id: str

    :rtype: ApiNote
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_notes(
            connexion.request, account_id)

        api_impl = api.get_api_impl()
        doc = api_impl.get_note(subject, account_id, provider_id, note_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while getting a note")
        return e.to_error()
    except Exception as e:
        logger.exception(
            "An unexpected error was encountered while getting a note")
        return exceptions.InternalServerError(str(e)).to_error()


def delete_note(account_id, provider_id, note_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param provider_id: First part of note &#x60;name&#x60;: providers/{provider_id}/notes/{note_id}
    :type provider_id: str
    :param note_id: Second part of note &#x60;name&#x60;: providers/{provider_id}/notes/{note_id}
    :type note_id: str

    :rtype: ApiEmpty
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_delete_notes(
            connexion.request, account_id)

        api_impl = api.get_api_impl()
        api_impl.delete_note(subject, account_id, provider_id, note_id)
        return common.build_result(http.HTTPStatus.OK, {})
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting a note")
        return e.to_error()
    except Exception as e:
        logger.exception(
            "An unexpected error was encountered while deleting a note")
        return exceptions.InternalServerError(str(e)).to_error()
