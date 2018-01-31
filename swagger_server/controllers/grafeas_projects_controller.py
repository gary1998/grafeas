import connexion
from swagger_server.models.api_empty import ApiEmpty
from swagger_server.models.api_list_projects_response import ApiListProjectsResponse
from swagger_server.models.api_project import ApiProject
from datetime import date, datetime
from typing import List, Dict
from swagger_server.util import deserialize_date, deserialize_datetime
from swagger_server.controllers.resources import get_store

def create_project(body):
    """
    Creates a new &#x60;Project&#x60;.
    
    :param body: 
    :type body: dict | bytes

    :rtype: ApiEmpty
    """
    if connexion.request.is_json:
        body = ApiProject.from_dict(connexion.request.get_json())
    store = get_store()
    return 'do some magic!'


def delete_project(projectId):
    """
    Deletes the given &#x60;Project&#x60; from the system.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str

    :rtype: ApiEmpty
    """
    store = get_store()
    return 'do some magic!'


def get_project(projectId):
    """
    Returns the requested &#x60;Project&#x60;.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str

    :rtype: ApiProject
    """
    store = get_store()
    return 'do some magic!'


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
    store = get_store()
    return 'do some magic!'


def update_project(projectId, body):
    """
    Updates an existing &#x60;Project&#x60;.
    
    :param projectId: Part of &#x60;parent&#x60;. This field contains the projectId for example: projects/{projectId}
    :type projectId: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiProject
    """
    if connexion.request.is_json:
        body = ApiProject.from_dict(connexion.request.get_json())
    store = get_store()
    return 'do some magic!'
