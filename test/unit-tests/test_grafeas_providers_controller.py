# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
from flask import json
from http import HTTPStatus
from .common_ut import BaseTestCase, TEST_ACCOUNT_ID

import os

import unittest
import threading


class TestGrafeasProvidersController(BaseTestCase):
    """ GrafeasProvidersController integration test stubs """

    def tearDown(self):
        for thread in threading.enumerate():
            if thread.name == "warm-cache":
                thread.cancel()

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_01_create_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """

        body = {
            "id": "Note03",
            "short_description": "The short description of Note03",
            "long_description": "The long description of Note03",
            "kind": "FINDING",
            "finding": {
                "severity": "HIGH"
            },
            "reported_by": {
                "id": "The reporter ID",
                "title": "The reporter title",
                "url": "The reporter URL"
            }
        }

        response = self.post_note(TEST_ACCOUNT_ID, 'ProviderX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_02_create_occurrence(self):
        """
        Test case for create_occurrence

        Creates a new `Occurrence`. Use this method to create `Occurrences` for a resource.
        """

        body = {
            "id": "Occurrence04",
            "note_name": "{}/providers/{}/notes/{}".format(TEST_ACCOUNT_ID, 'ProviderX', 'Note03'),
            "short_description": "The short description of Occurrence04",
            "long_description": "The long description of Occurrence04",
            "kind": "FINDING",
            "finding": {
                "certainty": "MEDIUM"
            },
            "context": {
                "resource_name": "Resource04"
            }
        }

        response = self.post_occurrence(TEST_ACCOUNT_ID, 'ProviderX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_03_list_providers(self):
        """
        Test case for list_providers

        Lists `Providers`
        """

        response = self.get_providers(TEST_ACCOUNT_ID)
        self.assertStatus(response, HTTPStatus.OK,
                          "Response body is : " + response.data.decode('utf-8'))
        result = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(result['providers']) > 0,
                        "An array of one or more providers was expected.")

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_04_delete_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """

        response = self.delete_occurrence(TEST_ACCOUNT_ID, 'ProviderX', 'Occurrence04')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    @unittest.skipIf(os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient',
                     "Skipping for security advisor")
    def test_05_delete_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """

        response = self.delete_note(TEST_ACCOUNT_ID, 'ProviderX', 'Note03')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
