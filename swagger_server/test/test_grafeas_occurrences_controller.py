# coding: utf-8

from . import BaseTestCase
from flask import json


class TestGrafeasOccurrencesController(BaseTestCase):
    """ GrafeasOccurrencesController integration test stubs """

    def test_create_occurrence(self):
        """
        Test case for create_occurrence

        Creates a new `Occurrence`. Use this method to create `Occurrences` for a resource.
        """
        body = ApiOccurrence()
        response = self.client.open('/v1alpha1/projects/{projectId}/occurrences'.format(projectId='projectId_example'),
                                    method='POST',
                                    data=json.dumps(body),
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_list_note_occurrences(self):
        """
        Test case for list_note_occurrences

        Lists `Occurrences` referencing the specified `Note`. Use this method to get all occurrences referencing your `Note` across all your customer projects.
        """
        query_string = [('filter', 'filter_example'),
                        ('page_size', 56),
                        ('page_token', 'page_token_example')]
        response = self.client.open('/v1alpha1/projects/{projectId}/notes/{noteId}/occurrences'.format(projectId='projectId_example', noteId='noteId_example'),
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_list_occurrences(self):
        """
        Test case for list_occurrences

        Lists active `Occurrences` for a given project matching the filters.
        """
        query_string = [('filter', 'filter_example'),
                        ('page_size', 56),
                        ('page_token', 'page_token_example')]
        response = self.client.open('/v1alpha1/projects/{projectId}/occurrences'.format(projectId='projectId_example'),
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
