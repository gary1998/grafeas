from . import BaseTestCase
from flask import json
from http import HTTPStatus


class TestGrafeasOccurrencesController(BaseTestCase):
    """ GrafeasOccurrencesController integration test stubs """

    def test_01_create_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """

        body = {
            "id": "Note02",
            "short_description": "The short description of Note02",
            "long_description": "The long description of Note02",
            "kind": "FINDING",
            "finding_type": {
                "default_severity": "HIGH"
            }
        }

        response = self.post_note('ProjectX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_02_create_duplicate_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """

        body = {
            "id": "Note02",
            "short_description": "The short description of Note02",
            "long_description": "The long description of Note02",
            "kind": "FINDING",
            "finding_type": {
                "default_severity": "MEDIUM"
            }
        }

        response = self.post_note('ProjectX', body)
        self.assertStatus(response, HTTPStatus.CONFLICT, "Response body is : " + response.data.decode('utf-8'))

    def test_03_create_occurrence(self):
        """
        Test case for create_occurrence

        Creates a new `Occurrence`. Use this method to create `Occurrences` for a resource.
        """

        body = {
            "id": "Occurrence02",
            "note_name": "projects/{}/notes/{}".format('ProjectX', 'Note02'),
            "short_description": "The short description of Occurrence02",
            "long_description": "The long description of Occurrence02",
            "kind": "FINDING",
            "finding": {
                "certainty": "MEDIUM"
            },
            "context": {
                "account_id": "AccountY"
            }
        }

        response = self.post_occurrence('ProjectX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_04_create_duplicate_occurrence(self):
        """
        Test case for create_occurrence

        Creates a new `Occurrence`. Use this method to create `Occurrences` for a resource.
        """

        body = {
            "id": "Occurrence02",
            "note_name": "projects/{}/notes/{}".format('ProjectX', 'Note02'),
            "short_description": "The short description of Occurrence02",
            "long_description": "The long description of Occurrence02",
            "kind": "FINDING",
            "finding": {
                "certainty": "HIGH"
            },
            "context": {
                "account_id": "AccountY"
            }
        }

        response = self.post_occurrence('ProjectX', body)
        self.assertStatus(response, HTTPStatus.CONFLICT, "Response body is : " + response.data.decode('utf-8'))

    def test_05_create_or_update_occurrence(self):
        """
        Test case for create_occurrence

        Creates a new `Occurrence`. Use this method to create `Occurrences` for a resource.
        """

        body = {
            "id": "Occurrence02",
            "note_name": "projects/{}/notes/{}".format('ProjectX', 'Note02'),
            "short_description": "Updated short description of Occurrence02",
            "long_description": "Updated long description of Occurrence02",
            "kind": "FINDING",
            "finding": {
                "certainty": "HIGH"
            },
            "context": {
                "account_id": "AccountY"
            }
        }

        response = self.post_or_put_occurrence('ProjectX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_06_get_occurrence(self):
        """
        Test case for get_note

        Returns the requested `Note`.
        """

        response = self.get_occurrence('ProjectX', 'Occurrence02')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_07_list_occurrences(self):
        """
        Test case for list_occurrences

        Lists active `Occurrences` for a given project matching the filters.
        """

        response = self.get_occurrences('ProjectX')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))
        results = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(results) > 0, "A array of one ore more occurrences was expected.")

    def test_08_list_note_occurrences(self):
        """
        Test case for list_note_occurrences

        Lists `Occurrences` referencing the specified `Note`.
        Use this method to get all occurrences referencing your `Note` across all your customer projects.
        """

        response = self.get_note_occurrences('ProjectX', 'Note02')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))
        results = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(results) > 0, "An array of one or more occurrences was expected.")

    def test_09_delete_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """

        response = self.delete_occurrence('ProjectX', 'Occurrence02')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_10_delete_missing_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """

        response = self.delete_occurrence('ProjectX', 'Occurrence02')
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))

    def test_11_delete_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """

        response = self.delete_note('ProjectX', 'Note02')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_12_delete_missing_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """

        response = self.delete_note('ProjectX', 'Note02')
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
