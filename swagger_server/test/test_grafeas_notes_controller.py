# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.api_list_notes_response import ApiListNotesResponse
from swagger_server.models.api_note import ApiNote
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestGrafeasNotesController(BaseTestCase):
    """ GrafeasNotesController integration test stubs """

    def test_create_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """
        body = ApiNote()
        response = self.client.open('/v1alpha1/projects/{projectId}/notes'.format(projectId='projectId_example'),
                                    method='POST',
                                    data=json.dumps(body),
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_occurrence_note(self):
        """
        Test case for get_occurrence_note

        Gets the `Note` attached to the given `Occurrence`.
        """
        response = self.client.open('/v1alpha1/projects/{projectId}/occurrences/{occurrenceId}/notes'.format(projectId='projectId_example', occurrenceId='occurrenceId_example'),
                                    method='GET',
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_list_notes(self):
        """
        Test case for list_notes

        Lists all `Notes` for a given project.
        """
        query_string = [('filter', 'filter_example'),
                        ('page_size', 56),
                        ('page_token', 'page_token_example')]
        response = self.client.open('/v1alpha1/projects/{projectId}/notes'.format(projectId='projectId_example'),
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
