# coding: utf-8

from __future__ import absolute_import
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class ApiProject(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, name: str=None):
        """
        ApiProject - a model defined in Swagger

        :param name: The name of this ApiProject.
        :type name: str
        """
        self.swagger_types = {
            'name': str
        }

        self.attribute_map = {
            'name': 'name'
        }

        self._name = name

    @classmethod
    def from_dict(cls, dikt) -> 'ApiProject':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The apiProject of this ApiProject.
        :rtype: ApiProject
        """
        return deserialize_model(dikt, cls)

    @property
    def name(self) -> str:
        """
        Gets the name of this ApiProject.

        :return: The name of this ApiProject.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """
        Sets the name of this ApiProject.

        :param name: The name of this ApiProject.
        :type name: str
        """

        self._name = name

