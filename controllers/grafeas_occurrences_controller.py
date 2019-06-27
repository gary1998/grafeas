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
import urllib.parse
from controllers import api
from controllers import auth
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.occurrences")


def create_occurrence(account_id, provider_id, body):
    """
    Creates a new &#x60;Occurrence&#x60;. Use this method to create &#x60;Occurrences&#x60; for a resource.

    :param provider_id: Part of &#x60;parent&#x60;. This contains the provider_id for example: providers/{provider_id}
    :type provider_id: str
    :param body:
    :type body: dict | bytes

    :rtype: ApiOccurrence
    """

    try:
        provider_id = urllib.parse.quote(provider_id, safe='')
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_write_occurrences(connexion.request, account_id)

        api_impl = api.get_api_impl()
        occurrence_id = body['id']
        replace_if_exists = connexion.request.headers.get('Replace-If-Exists', 'false').lower()
        mode = 'replace' if replace_if_exists == 'true' else 'create'
        doc = api_impl.write_occurrence(subject, account_id, provider_id, occurrence_id, body, mode)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while creating an occurrence")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while creating an occurrence")
        return exceptions.InternalServerError(str(e)).to_error()


def update_occurrence(account_id, provider_id, occurrence_id, body):
    """
    Updates an existing &#x60;Note&#x60;.

    :param provider_id: First part of occurrence &#x60;name&#x60;: providers/{provider_id}/notes/{occurrence_id}
    :type provider_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: providers/{provider_id}/notes/{occurrence_id}
    :type occurrence_id: str
    :param body:
    :type body: dict | bytes

    :rtype: ApiNote
    """

    try:
        provider_id = urllib.parse.quote(provider_id, safe='')
        occurrence_id = urllib.parse.quote(occurrence_id, safe='')
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_write_occurrences(connexion.request, account_id)

        api_impl = api.get_api_impl()
        doc = api_impl.write_occurrence(subject, account_id, provider_id, occurrence_id, body, mode='update')
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while updating an occurrence")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while updating a occurrence")
        return exceptions.InternalServerError(str(e)).to_error()


def list_occurrences(account_id, provider_id, filter=None, page_size=None, page_token=None):
    """
    Lists active &#x60;Occurrences&#x60; for a given provider matching the filters.

    :param provider_id: Part of &#x60;parent&#x60;. This contains the provider_id for example: providers/{provider_id}
    :type provider_id: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of occurrences to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListOccurrencesResponse
    """

    try:
        provider_id = urllib.parse.quote(provider_id, safe='')
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_occurrences(connexion.request, account_id)

        api_impl = api.get_api_impl()
        result = api_impl.list_occurrences(subject, account_id, provider_id, filter, page_size, page_token)
        return common.build_result(
            http.HTTPStatus.OK,
            {
                "occurrences": result.docs,
                "next_page_token": result.bookmark
            })
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing occurrences")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while listing occurrences")
        return exceptions.InternalServerError(str(e)).to_error()


def list_note_occurrences(account_id, provider_id, note_id, filter=None, page_size=None, page_token=None):
    """
    Lists &#x60;Occurrences&#x60; referencing the specified &#x60;Note&#x60;.
    Use this method to get all occurrences referencing your &#x60;Note&#x60; across all your customer providers.

    :param provider_id: First part of note &#x60;name&#x60;: providers/{provider_id}/notes/{note_id}
    :type provider_id: str
    :param note_id: Second part of note &#x60;name&#x60;: providers/{provider_id}/notes/{note_id}
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
        provider_id = urllib.parse.quote(provider_id, safe='')
        note_id = urllib.parse.quote(note_id,safe='')
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_occurrences(connexion.request, account_id)

        api_impl = api.get_api_impl()
        result = api_impl.list_note_occurrences(subject, account_id, provider_id, note_id,
                                                filter, page_size, page_token)
        return common.build_result(
            http.HTTPStatus.OK,
            {
                "occurrences": result.docs,
                "next_page_token": result.bookmark
            })
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing note occurrences")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while listing note occurrences")
        return exceptions.InternalServerError(str(e)).to_error()


def get_occurrence(account_id, provider_id, occurrence_id):
    """
    Returns the requested &#x60;Note&#x60;.

    :param provider_id: First part of occurrence &#x60;name&#x60;: providers/{provider_id}/notes/{occurrence_id}
    :type provider_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: providers/{provider_id}/notes/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiOccurrence
    """

    try:
        provider_id = urllib.parse.quote(provider_id, safe='')
        occurrence_id = urllib.parse.quote(occurrence_id, safe='')
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_occurrences(connexion.request, account_id)

        api_impl = api.get_api_impl()
        doc = api_impl.get_occurrence(subject, account_id, provider_id, occurrence_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while getting an occurrence")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while getting an occurrence")
        return exceptions.InternalServerError(str(e)).to_error()


def delete_occurrence(account_id, provider_id, occurrence_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param provider_id: First part of occurrence &#x60;name&#x60;: providers/{provider_id}/occurrences/{occurrence_id}
    :type provider_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: providers/{provider_id}/occurrences/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiEmpty
    """

    try:
        provider_id = urllib.parse.quote(provider_id, safe='')
        occurrence_id = urllib.parse.quote(occurrence_id, safe='')
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_delete_occurrences(connexion.request, account_id)

        api_impl = api.get_api_impl()
        doc = api_impl.delete_occurrence(subject, account_id, provider_id, occurrence_id)
        return common.build_result(http.HTTPStatus.OK, doc)
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting an occurrence")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while deleting an occurrence")
        return exceptions.InternalServerError(str(e)).to_error()
