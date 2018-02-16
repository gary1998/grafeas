from . import BaseTestCase
from flask import json
from http import HTTPStatus


class TestGrafeasNotesController(BaseTestCase):
    """ GrafeasNotesController integration test stubs """

    def test_01_create_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """

        body = {
            "id": "Note01",
            "short_description": "The short description of Note01",
            "long_description": "The long description of Note01"
        }

        response = self.post_note('ProjectX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_02_create_duplicate_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """

        body = {
            "id": "Note01",
            "short_description": "The short description of Note01",
            "long_description": "The long description of Note01"
        }

        response = self.post_note('ProjectX', body)
        self.assertStatus(response, HTTPStatus.CONFLICT, "Response body is : " + response.data.decode('utf-8'))

    def test_03_get_note(self):
        """
        Test case for get_note

        Returns the requested `Note`.
        """

        response = self.get_note('ProjectX', 'Note01')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_04_list_notes(self):
        """
        Test case for list_notes

        Lists all `Notes` for a given project.
        """

        response = self.get_notes('ProjectX')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))
        results = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(results) > 0, "An array of one or more notes was expected.")

    def test_05_create_occurrence(self):
        """
        Test case for create_occurrece

        Returns the requested `Note`.
        """

        body = {
            "id": "Occurrence01",
            "note_name": "projects/{}/notes/{}".format('ProjectX', 'Note01'),
            "short_description": "The short description of Occurrence01",
            "long_description": "The long description of Occurrence01"
        }

        response = self.post_occurrence('ProjectX', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_06_create_duplicate_occurrence(self):
        """
        Test case for create_occurrece

        Returns the requested `Note`.
        """

        body = {
            "id": "Occurrence01",
            "note_name": "projects/{}/notes/{}".format('ProjectX', 'Note01'),
            "short_description": "The short description of Occurrence01",
            "long_description": "The long description of Occurrence01"
        }

        response = self.post_occurrence('ProjectX', body)
        self.assertStatus(response, HTTPStatus.CONFLICT, "Response body is : " + response.data.decode('utf-8'))

    def test_07_get_occurrence_note(self):
        """
        Test case for get_occurrence_note

        Gets the `Note` attached to the given `Occurrence`.
        """
        response = self.get_occurrence_note('ProjectX', 'Occurrence01')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_08_update_note(self):
        """
        Test case for update_note

        Updates an existing `Note`.
        """

        body = {
            "id": "Note01",
            "short_description": "The updated short description of Note01",
            "long_description": "The updated long description of Note01"
        }

        response = self.put_note('ProjectX', 'Note01', body)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_09_delete_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """
        response = self.delete_note('ProjectX', 'Note01')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_10_delete_missing_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """
        response = self.delete_note('ProjectX', 'Note01')
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))

    def test_11_delete_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """
        response = self.delete_occurrence('ProjectX', 'Occurrence01')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_12_delete_missing_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """
        response = self.delete_occurrence('ProjectX', 'Occurrence01')
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
