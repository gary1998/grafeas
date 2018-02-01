# coding: utf-8

from . import BaseTestCase
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

    def test_delete_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """
        response = self.client.open('/v1alpha1/projects/{projectId}/notes/{noteId}'.format(projectId='projectId_example', noteId='noteId_example'),
                                    method='DELETE',
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_note(self):
        """
        Test case for get_note

        Returns the requested `Note`.
        """
        response = self.client.open('/v1alpha1/projects/{projectId}/notes/{noteId}'.format(projectId='projectId_example', noteId='noteId_example'),
                                    method='GET',
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

    def test_update_note(self):
        """
        Test case for update_note

        Updates an existing `Note`.
        """
        body = ApiNote()
        response = self.client.open('/v1alpha1/projects/{projectId}/notes/{noteId}'.format(projectId='projectId_example', noteId='noteId_example'),
                                    method='PUT',
                                    data=json.dumps(body),
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
