# coding: utf-8

from __future__ import absolute_import
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class ApiRepoSource(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, project_id: str=None, repo_name: str=None, branch_name: str=None, tag_name: str=None, commit_sha: str=None):
        """
        ApiRepoSource - a model defined in Swagger

        :param project_id: The project_id of this ApiRepoSource.
        :type project_id: str
        :param repo_name: The repo_name of this ApiRepoSource.
        :type repo_name: str
        :param branch_name: The branch_name of this ApiRepoSource.
        :type branch_name: str
        :param tag_name: The tag_name of this ApiRepoSource.
        :type tag_name: str
        :param commit_sha: The commit_sha of this ApiRepoSource.
        :type commit_sha: str
        """
        self.swagger_types = {
            'project_id': str,
            'repo_name': str,
            'branch_name': str,
            'tag_name': str,
            'commit_sha': str
        }

        self.attribute_map = {
            'project_id': 'projectId',
            'repo_name': 'repo_name',
            'branch_name': 'branch_name',
            'tag_name': 'tag_name',
            'commit_sha': 'commit_sha'
        }

        self._project_id = project_id
        self._repo_name = repo_name
        self._branch_name = branch_name
        self._tag_name = tag_name
        self._commit_sha = commit_sha

    @classmethod
    def from_dict(cls, dikt) -> 'ApiRepoSource':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The apiRepoSource of this ApiRepoSource.
        :rtype: ApiRepoSource
        """
        return deserialize_model(dikt, cls)

    @property
    def project_id(self) -> str:
        """
        Gets the project_id of this ApiRepoSource.
        ID of the project that owns the repo.

        :return: The project_id of this ApiRepoSource.
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id: str):
        """
        Sets the project_id of this ApiRepoSource.
        ID of the project that owns the repo.

        :param project_id: The project_id of this ApiRepoSource.
        :type project_id: str
        """

        self._project_id = project_id

    @property
    def repo_name(self) -> str:
        """
        Gets the repo_name of this ApiRepoSource.
        Name of the repo.

        :return: The repo_name of this ApiRepoSource.
        :rtype: str
        """
        return self._repo_name

    @repo_name.setter
    def repo_name(self, repo_name: str):
        """
        Sets the repo_name of this ApiRepoSource.
        Name of the repo.

        :param repo_name: The repo_name of this ApiRepoSource.
        :type repo_name: str
        """

        self._repo_name = repo_name

    @property
    def branch_name(self) -> str:
        """
        Gets the branch_name of this ApiRepoSource.
        Name of the branch to build.

        :return: The branch_name of this ApiRepoSource.
        :rtype: str
        """
        return self._branch_name

    @branch_name.setter
    def branch_name(self, branch_name: str):
        """
        Sets the branch_name of this ApiRepoSource.
        Name of the branch to build.

        :param branch_name: The branch_name of this ApiRepoSource.
        :type branch_name: str
        """

        self._branch_name = branch_name

    @property
    def tag_name(self) -> str:
        """
        Gets the tag_name of this ApiRepoSource.
        Name of the tag to build.

        :return: The tag_name of this ApiRepoSource.
        :rtype: str
        """
        return self._tag_name

    @tag_name.setter
    def tag_name(self, tag_name: str):
        """
        Sets the tag_name of this ApiRepoSource.
        Name of the tag to build.

        :param tag_name: The tag_name of this ApiRepoSource.
        :type tag_name: str
        """

        self._tag_name = tag_name

    @property
    def commit_sha(self) -> str:
        """
        Gets the commit_sha of this ApiRepoSource.
        Explicit commit SHA to build.

        :return: The commit_sha of this ApiRepoSource.
        :rtype: str
        """
        return self._commit_sha

    @commit_sha.setter
    def commit_sha(self, commit_sha: str):
        """
        Sets the commit_sha of this ApiRepoSource.
        Explicit commit SHA to build.

        :param commit_sha: The commit_sha of this ApiRepoSource.
        :type commit_sha: str
        """

        self._commit_sha = commit_sha

