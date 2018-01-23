# coding: utf-8

from __future__ import absolute_import
from swagger_server.models.api_note import ApiNote
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class ApiListNotesResponse(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, notes: List[ApiNote]=None, next_page_token: str=None):
        """
        ApiListNotesResponse - a model defined in Swagger

        :param notes: The notes of this ApiListNotesResponse.
        :type notes: List[ApiNote]
        :param next_page_token: The next_page_token of this ApiListNotesResponse.
        :type next_page_token: str
        """
        self.swagger_types = {
            'notes': List[ApiNote],
            'next_page_token': str
        }

        self.attribute_map = {
            'notes': 'notes',
            'next_page_token': 'next_page_token'
        }

        self._notes = notes
        self._next_page_token = next_page_token

    @classmethod
    def from_dict(cls, dikt) -> 'ApiListNotesResponse':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The apiListNotesResponse of this ApiListNotesResponse.
        :rtype: ApiListNotesResponse
        """
        return deserialize_model(dikt, cls)

    @property
    def notes(self) -> List[ApiNote]:
        """
        Gets the notes of this ApiListNotesResponse.

        :return: The notes of this ApiListNotesResponse.
        :rtype: List[ApiNote]
        """
        return self._notes

    @notes.setter
    def notes(self, notes: List[ApiNote]):
        """
        Sets the notes of this ApiListNotesResponse.

        :param notes: The notes of this ApiListNotesResponse.
        :type notes: List[ApiNote]
        """

        self._notes = notes

    @property
    def next_page_token(self) -> str:
        """
        Gets the next_page_token of this ApiListNotesResponse.
        The next pagination token in the list response. It should be used as page_token for the following request. An empty value means no more result.

        :return: The next_page_token of this ApiListNotesResponse.
        :rtype: str
        """
        return self._next_page_token

    @next_page_token.setter
    def next_page_token(self, next_page_token: str):
        """
        Sets the next_page_token of this ApiListNotesResponse.
        The next pagination token in the list response. It should be used as page_token for the following request. An empty value means no more result.

        :param next_page_token: The next_page_token of this ApiListNotesResponse.
        :type next_page_token: str
        """

        self._next_page_token = next_page_token

