# coding: utf-8

from __future__ import absolute_import
from swagger_server.models.operation import Operation
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class ApiCreateOperationRequest(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, parent: str=None, operation_id: str=None, operation: Operation=None):
        """
        ApiCreateOperationRequest - a model defined in Swagger

        :param parent: The parent of this ApiCreateOperationRequest.
        :type parent: str
        :param operation_id: The operation_id of this ApiCreateOperationRequest.
        :type operation_id: str
        :param operation: The operation of this ApiCreateOperationRequest.
        :type operation: Operation
        """
        self.swagger_types = {
            'parent': str,
            'operation_id': str,
            'operation': Operation
        }

        self.attribute_map = {
            'parent': 'parent',
            'operation_id': 'operation_id',
            'operation': 'operation'
        }

        self._parent = parent
        self._operation_id = operation_id
        self._operation = operation

    @classmethod
    def from_dict(cls, dikt) -> 'ApiCreateOperationRequest':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The apiCreateOperationRequest of this ApiCreateOperationRequest.
        :rtype: ApiCreateOperationRequest
        """
        return deserialize_model(dikt, cls)

    @property
    def parent(self) -> str:
        """
        Gets the parent of this ApiCreateOperationRequest.
        The projectId that this operation should be created under.

        :return: The parent of this ApiCreateOperationRequest.
        :rtype: str
        """
        return self._parent

    @parent.setter
    def parent(self, parent: str):
        """
        Sets the parent of this ApiCreateOperationRequest.
        The projectId that this operation should be created under.

        :param parent: The parent of this ApiCreateOperationRequest.
        :type parent: str
        """

        self._parent = parent

    @property
    def operation_id(self) -> str:
        """
        Gets the operation_id of this ApiCreateOperationRequest.
        The ID to use for this operation.

        :return: The operation_id of this ApiCreateOperationRequest.
        :rtype: str
        """
        return self._operation_id

    @operation_id.setter
    def operation_id(self, operation_id: str):
        """
        Sets the operation_id of this ApiCreateOperationRequest.
        The ID to use for this operation.

        :param operation_id: The operation_id of this ApiCreateOperationRequest.
        :type operation_id: str
        """

        self._operation_id = operation_id

    @property
    def operation(self) -> Operation:
        """
        Gets the operation of this ApiCreateOperationRequest.
        The operation to create.

        :return: The operation of this ApiCreateOperationRequest.
        :rtype: Operation
        """
        return self._operation

    @operation.setter
    def operation(self, operation: Operation):
        """
        Sets the operation of this ApiCreateOperationRequest.
        The operation to create.

        :param operation: The operation of this ApiCreateOperationRequest.
        :type operation: Operation
        """

        self._operation = operation

