# coding: utf-8

from __future__ import absolute_import
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class ApiProjectRepoId(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, project_id: str=None, repo_name: str=None):
        """
        ApiProjectRepoId - a model defined in Swagger

        :param project_id: The project_id of this ApiProjectRepoId.
        :type project_id: str
        :param repo_name: The repo_name of this ApiProjectRepoId.
        :type repo_name: str
        """
        self.swagger_types = {
            'project_id': str,
            'repo_name': str
        }

        self.attribute_map = {
            'project_id': 'projectId',
            'repo_name': 'repo_name'
        }

        self._project_id = project_id
        self._repo_name = repo_name

    @classmethod
    def from_dict(cls, dikt) -> 'ApiProjectRepoId':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The apiProjectRepoId of this ApiProjectRepoId.
        :rtype: ApiProjectRepoId
        """
        return deserialize_model(dikt, cls)

    @property
    def project_id(self) -> str:
        """
        Gets the project_id of this ApiProjectRepoId.
        The ID of the project.

        :return: The project_id of this ApiProjectRepoId.
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id: str):
        """
        Sets the project_id of this ApiProjectRepoId.
        The ID of the project.

        :param project_id: The project_id of this ApiProjectRepoId.
        :type project_id: str
        """

        self._project_id = project_id

    @property
    def repo_name(self) -> str:
        """
        Gets the repo_name of this ApiProjectRepoId.
        The name of the repo. Leave empty for the default repo.

        :return: The repo_name of this ApiProjectRepoId.
        :rtype: str
        """
        return self._repo_name

    @repo_name.setter
    def repo_name(self, repo_name: str):
        """
        Sets the repo_name of this ApiProjectRepoId.
        The name of the repo. Leave empty for the default repo.

        :param repo_name: The repo_name of this ApiProjectRepoId.
        :type repo_name: str
        """

        self._repo_name = repo_name

