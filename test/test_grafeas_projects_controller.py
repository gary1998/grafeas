# coding: utf-8

from . import BaseTestCase
from flask import json


class TestGrafeasProjectsController(BaseTestCase):
    """ GrafeasProjectsController integration test stubs """

    def test_create_project(self):
        """
        Test case for create_project

        Creates a new `Project`.
        """
        body = ApiProject()
        response = self.client.open('/v1alpha1/projects',
                                    method='POST',
                                    data=json.dumps(body),
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_delete_project(self):
        """
        Test case for delete_project

        Deletes the given `Project` from the system.
        """
        response = self.client.open('/v1alpha1/projects/{projectId}'.format(projectId='projectId_example'),
                                    method='DELETE',
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_project(self):
        """
        Test case for get_project

        Returns the requested `Project`.
        """
        response = self.client.open('/v1alpha1/projects/{projectId}'.format(projectId='projectId_example'),
                                    method='GET',
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_list_projects(self):
        """
        Test case for list_projects

        Lists `Projects`
        """
        query_string = [('filter', 'filter_example'),
                        ('page_size', 56),
                        ('page_token', 'page_token_example')]
        response = self.client.open('/v1alpha1/projects',
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_update_project(self):
        """
        Test case for update_project

        Updates an existing `Project`.
        """
        body = ApiProject()
        response = self.client.open('/v1alpha1/projects/{projectId}'.format(projectId='projectId_example'),
                                    method='PUT',
                                    data=json.dumps(body),
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
