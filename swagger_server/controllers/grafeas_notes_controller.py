import connexion
from swagger_server.models.api_list_notes_response import ApiListNotesResponse
from swagger_server.models.api_note import ApiNote
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def create_note(projectId, body):
    """
    Creates a new &#x60;Note&#x60;.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: \&quot;projects/{projectId}
    :type projectId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """
    if connexion.request.is_json:
        body = ApiNote.from_dict(connexion.request.get_json())
    return 'do some magic!'


def get_occurrence_note(projectId, occurrenceId):
    """
    Gets the &#x60;Note&#x60; attached to the given &#x60;Occurrence&#x60;.
    
    :param projectId: Part of &#x60;name&#x60;. The name of the occurrence in the form \&quot;projects/{projectId}/occurrences/{occurrenceId}\&quot;
    :type projectId: str
    :param occurrenceId: Part of &#x60;name&#x60;. See documentation of &#x60;projectId&#x60;.
    :type occurrenceId: str

    :rtype: ApiNote
    """
    return 'do some magic!'


def list_notes(projectId, filter=None, page_size=None, page_token=None):
    """
    Lists all &#x60;Notes&#x60; for a given project.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: \&quot;projects/{projectId}
    :type projectId: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNotesResponse
    """
    return 'do some magic!'
