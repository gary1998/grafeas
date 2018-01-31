import connexion
from swagger_server.models.api_empty import ApiEmpty
from swagger_server.models.api_list_notes_response import ApiListNotesResponse
from swagger_server.models.api_note import ApiNote
from datetime import date, datetime
from typing import List, Dict
from swagger_server.util import deserialize_date, deserialize_datetime
from swagger_server.controllers.resources import get_store

def create_note(projectId, body):
    """
    Creates a new &#x60;Note&#x60;.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """
    if connexion.request.is_json:
        body = ApiNote.from_dict(connexion.request.get_json())
    store = get_store()
    return 'do some magic!'


def delete_note(projectId, noteId):
    """
    Deletes the given &#x60;Note&#x60; from the system.
    
    :param projectId: First part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type projectId: str
    :param noteId: Second part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type noteId: str

    :rtype: ApiEmpty
    """
    store = get_store()
    return 'do some magic!'


def get_note(projectId, noteId):
    """
    Returns the requested &#x60;Note&#x60;.
    
    :param projectId: First part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type projectId: str
    :param noteId: Second part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type noteId: str

    :rtype: ApiNote
    """
    store = get_store()
    return 'do some magic!'


def get_occurrence_note(projectId, occurrenceId):
    """
    Gets the &#x60;Note&#x60; attached to the given &#x60;Occurrence&#x60;.
    
    :param projectId: First part of occurrence &#x60;name&#x60;: projects/{projectId}/occurrences/{occurrenceId}
    :type projectId: str
    :param occurrenceId: Second part of occurrence &#x60;name&#x60;: projects/{projectId}/occurrences/{occurrenceId}
    :type occurrenceId: str

    :rtype: ApiNote
    """
    store = get_store()
    return 'do some magic!'


def list_notes(projectId, filter=None, page_size=None, page_token=None):
    """
    Lists all &#x60;Notes&#x60; for a given project.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNotesResponse
    """
    store = get_store()
    return 'do some magic!'


def update_note(projectId, noteId, body):
    """
    Updates an existing &#x60;Note&#x60;.
    
    :param projectId: First part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type projectId: str
    :param noteId: Second part of note &#x60;name&#x60;: projects/{projectId}/notes/{noteId}
    :type noteId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiNote
    """
    if connexion.request.is_json:
        body = ApiNote.from_dict(connexion.request.get_json())
    store = get_store()
    return 'do some magic!'
