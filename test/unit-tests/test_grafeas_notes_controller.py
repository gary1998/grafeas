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
import threading


class TestGrafeasNotesController(BaseTestCase):
    """ GrafeasNotesController integration test stubs """

    def tearDown(self):
        for thread in threading.enumerate():
            if thread.name == "warm-cache":
                thread.cancel()
                
    def test_01_create_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """

        body = {
            "id": "Note01",
            "short_description": "The short description of Note01",
            "long_description": "The long description of Note01",
            "kind": "FINDING",
            "finding": {
                "severity": "HIGH"
            },
            "reported_by": {
                "id": "The ID of the reporter",
                "title": "The title of the reporter",
                "url": "The url of the reporter"
            }
        }

        response = self.post_note(TEST_ACCOUNT_ID, 'ProviderX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_02_create_duplicate_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """

        body = {
            "id": "Note01",
            "short_description": "The short description of Note01",
            "long_description": "The long description of Note01",
            "kind": "FINDING",
            "finding": {
                "severity": "HIGH"
            },
            "reported_by": {
                "id": "The ID of the reporter",
                "title": "The title of the reporter",
                "url": "The url of the reporter"
            }
        }

        response = self.post_note(TEST_ACCOUNT_ID, 'ProviderX', body)
        self.assertStatus(response, HTTPStatus.CONFLICT, "Response body is : " + response.data.decode('utf-8'))

    def test_03_get_note(self):
        """
        Test case for get_note

        Returns the requested `Note`.
        """

        response = self.get_note(TEST_ACCOUNT_ID, 'ProviderX', 'Note01')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_04_list_notes(self):
        """
        Test case for list_notes

        Lists all `Notes` for a given provider.
        """

        response = self.get_notes(TEST_ACCOUNT_ID, 'ProviderX')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))
        result = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(result['notes']) > 0, "An array of one or more notes was expected.")

    def test_05_create_occurrence(self):
        """
        Test case for create_occurrece

        Returns the requested `Note`.
        """

        body = {
            "id": "Occurrence01",
            "note_name": "{}/providers/{}/notes/{}".format(TEST_ACCOUNT_ID, 'ProviderX', 'Note01'),
            "short_description": "The short description of Occurrence01",
            "long_description": "The long description of Occurrence01",
            "kind": "FINDING",
            "finding": {
                "certainty": "HIGH"
            },
            "context": {
                "resource_name": "Resource01"
            }
        }

        response = self.post_occurrence(TEST_ACCOUNT_ID, 'ProviderX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_06_create_duplicate_occurrence(self):
        """
        Test case for create_occurrece

        Returns the requested `Note`.
        """

        body = {
            "id": "Occurrence01",
            "note_name": "{}/providers/{}/notes/{}".format(TEST_ACCOUNT_ID, 'ProviderX', 'Note01'),
            "short_description": "The short description of Occurrence01",
            "long_description": "The long description of Occurrence01",
            "kind": "FINDING",
            "finding": {
                "certainty": "HIGH"
            },
            "context": {
                "resource_name": "Resource01"
            }
        }

        response = self.post_occurrence(TEST_ACCOUNT_ID, 'ProviderX', body)
        self.assertStatus(response, HTTPStatus.CONFLICT, "Response body is : " + response.data.decode('utf-8'))

    def test_07_get_occurrence_note(self):
        """
        Test case for get_occurrence_note

        Gets the `Note` attached to the given `Occurrence`.
        """
        response = self.get_occurrence_note(TEST_ACCOUNT_ID, 'ProviderX', 'Occurrence01')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_08_update_note(self):
        """
        Test case for update_note

        Updates an existing `Note`.
        """

        body = {
            "id": "Note01",
            "kind": "FINDING",
            "short_description": "The updated short description of Note01",
            "long_description": "The updated long description of Note01",
            "finding": {
                "severity": "MEDIUM",
                "certainty": "LOW"
            },
            "reported_by": {
                "id": "The ID of the reporter",
                "title": "The title of the reporter",
                "url": "The url of the reporter"
            }
        }

        response = self.put_note(TEST_ACCOUNT_ID, 'ProviderX', 'Note01', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_09_delete_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """
        response = self.delete_note(TEST_ACCOUNT_ID, 'ProviderX', 'Note01')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_10_delete_missing_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """
        response = self.delete_note(TEST_ACCOUNT_ID, 'ProviderX', 'Note01')
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))

    def test_11_delete_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """
        response = self.delete_occurrence(TEST_ACCOUNT_ID, 'ProviderX', 'Occurrence01')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_12_delete_missing_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """
        response = self.delete_occurrence(TEST_ACCOUNT_ID, 'ProviderX', 'Occurrence01')
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
