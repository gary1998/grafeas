import connexion
from swagger_server.models.api_list_note_occurrences_response import ApiListNoteOccurrencesResponse
from swagger_server.models.api_list_occurrences_response import ApiListOccurrencesResponse
from swagger_server.models.api_occurrence import ApiOccurrence
from datetime import date, datetime
from typing import List, Dict
from swagger_server.util import deserialize_date, deserialize_datetime
from swagger_server.controllers.resources import get_store

def create_occurrence(projectId, body):
    """
    Creates a new &#x60;Occurrence&#x60;. Use this method to create &#x60;Occurrences&#x60; for a resource.
    
    :param projectId: Part of &#x60;parent&#x60;. This contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiOccurrence
    """
    if connexion.request.is_json:
        body = ApiOccurrence.from_dict(connexion.request.get_json())
    store = get_store()
    return 'do some magic!'


def list_note_occurrences(projectId, noteId, filter=None, page_size=None, page_token=None):
    """
    Lists &#x60;Occurrences&#x60; referencing the specified &#x60;Note&#x60;. Use this method to get all occurrences referencing your &#x60;Note&#x60; across all your customer projects.
    
    :param projectId: First part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type projectId: str
    :param noteId: Second part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type noteId: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNoteOccurrencesResponse
    """
    store = get_store()
    return 'do some magic!'


def list_occurrences(projectId, filter=None, page_size=None, page_token=None):
    """
    Lists active &#x60;Occurrences&#x60; for a given project matching the filters.
    
    :param projectId: Part of &#x60;parent&#x60;. This contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of occurrences to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListOccurrencesResponse
    """
    store = get_store()
    return 'do some magic!'
