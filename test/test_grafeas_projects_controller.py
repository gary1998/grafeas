# coding: utf-8

from . import BaseTestCase
from flask import json


class TestGrafeasProjectsController(BaseTestCase):
    """ GrafeasProjectsController integration test stubs """

    def test_01_create_project(self):
        """
        Test case for create_project

        Creates a new `Project`.
        """

        body = {
            "project_id": "security-advisor"
        }

        response = self.client.open(
            path='/v1alpha1/projects',
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_02_get_project(self):
        """
        Test case for get_project

        Returns the requested `Project`.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}'.format("security-advisor"),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_03_list_projects(self):
        """
        Test case for list_projects

        Lists `Projects`
        """

        response = self.client.open(
            path='/v1alpha1/projects',
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
        results = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(results), 1, "An array of one project was expected.")

    def test_04_delete_project(self):
        """
        Test case for delete_project

        Deletes the given `Project` from the system.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}'.format("security-advisor"),
            method='DELETE',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
