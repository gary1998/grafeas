from flask import json
from http import HTTPStatus
from .common_ut import BaseTestCase, TEST_ACCOUNT_ID

import os

import unittest


class TestGrafeasProjectsController(BaseTestCase):
    """ GrafeasProjectsController integration test stubs """

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_01_create_project(self):
        """
        Test case for create_project

        Creates a new `Project`.
        """

        body = {
            "id": "ProjectX"
        }

        response = self.post_project(TEST_ACCOUNT_ID, body)
        self.assertStatus(response, HTTPStatus.OK,
                          "Response body is : " + response.data.decode('utf-8'))

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_02_create_duplicate_project(self):
        """
        Test case for create_project

        Creates a new `Project`.
        """

        body = {
            "id": "ProjectX"
        }

        response = self.post_project(TEST_ACCOUNT_ID, body)
        self.assertStatus(response, HTTPStatus.CONFLICT,
                          "Response body is : " + response.data.decode('utf-8'))

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_03_get_project(self):
        """
        Test case for get_project

        Returns the requested `Project`.
        """

        response = self.get_project(TEST_ACCOUNT_ID, "ProjectX")
        self.assertStatus(response, HTTPStatus.OK,
                          "Response body is : " + response.data.decode('utf-8'))

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_04_list_projects(self):
        """
        Test case for list_projects

        Lists `Projects`
        """

        response = self.get_projects(TEST_ACCOUNT_ID)
        self.assertStatus(response, HTTPStatus.OK,
                          "Response body is : " + response.data.decode('utf-8'))
        result = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(result['projects']) > 0,
                        "An array of one or more projects was expected.")

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_05_delete_project(self):
        """
        Test case for delete_project

        Deletes the given `Project` from the system.
        """

        response = self.delete_project(TEST_ACCOUNT_ID, "ProjectX")
        self.assertStatus(response, HTTPStatus.OK,
                          "Response body is : " + response.data.decode('utf-8'))

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_06_delete_missing_project(self):
        """
        Test case for delete_project

        Deletes the given `Project` from the system.
        """

        response = self.delete_project(TEST_ACCOUNT_ID, "ProjectX")
        self.assertStatus(response, HTTPStatus.NOT_FOUND,
                          "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
