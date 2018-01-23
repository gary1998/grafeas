# coding: utf-8

from __future__ import absolute_import
from swagger_server.models.api_note_kind import ApiNoteKind
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class ApiDiscovery(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, analysis_kind: ApiNoteKind=None):
        """
        ApiDiscovery - a model defined in Swagger

        :param analysis_kind: The analysis_kind of this ApiDiscovery.
        :type analysis_kind: ApiNoteKind
        """
        self.swagger_types = {
            'analysis_kind': ApiNoteKind
        }

        self.attribute_map = {
            'analysis_kind': 'analysis_kind'
        }

        self._analysis_kind = analysis_kind

    @classmethod
    def from_dict(cls, dikt) -> 'ApiDiscovery':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The apiDiscovery of this ApiDiscovery.
        :rtype: ApiDiscovery
        """
        return deserialize_model(dikt, cls)

    @property
    def analysis_kind(self) -> ApiNoteKind:
        """
        Gets the analysis_kind of this ApiDiscovery.
        The kind of analysis that is handled by this discovery.

        :return: The analysis_kind of this ApiDiscovery.
        :rtype: ApiNoteKind
        """
        return self._analysis_kind

    @analysis_kind.setter
    def analysis_kind(self, analysis_kind: ApiNoteKind):
        """
        Sets the analysis_kind of this ApiDiscovery.
        The kind of analysis that is handled by this discovery.

        :param analysis_kind: The analysis_kind of this ApiDiscovery.
        :type analysis_kind: ApiNoteKind
        """

        self._analysis_kind = analysis_kind

