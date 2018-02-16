from . import BaseTestCase
from flask import json
from http import HTTPStatus


class TestGrafeasProjectsController(BaseTestCase):
    """ GrafeasProjectsController integration test stubs """

    def test_01_create_project(self):
        """
        Test case for create_project

        Creates a new `Project`.
        """

        body = {
            "id": "ProjectX"
        }

        response = self.post_project(body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_02_create_duplicate_project(self):
        """
        Test case for create_project

        Creates a new `Project`.
        """

        body = {
            "id": "ProjectX"
        }

        response = self.post_project(body)
        self.assertStatus(response, HTTPStatus.CONFLICT, "Response body is : " + response.data.decode('utf-8'))

    def test_03_get_project(self):
        """
        Test case for get_project

        Returns the requested `Project`.
        """

        response = self.get_project("ProjectX")
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_04_list_projects(self):
        """
        Test case for list_projects

        Lists `Projects`
        """

        response = self.get_projects()
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))
        results = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(results) > 0, "An array of one or more projects was expected.")

    def test_05_delete_project(self):
        """
        Test case for delete_project

        Deletes the given `Project` from the system.
        """

        response = self.delete_project("ProjectX")
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_06_delete_missing_project(self):
        """
        Test case for delete_project

        Deletes the given `Project` from the system.
        """

        response = self.delete_project("ProjectX")
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
