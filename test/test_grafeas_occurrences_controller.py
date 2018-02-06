# coding: utf-8

from . import BaseTestCase
from flask import json


class TestGrafeasOccurrencesController(BaseTestCase):
    """ GrafeasOccurrencesController integration test stubs """

    def test_01_create_note(self):
        """
        Test case for create_note

        Creates a new `Note`.
        """

        body = {
            "note_id": "Note01",
            "short_description": "The short description of Note01",
            "long_description": "The long description of Note01"
        }

        response = self.client.open(
            path='/v1alpha1/projects/{}/notes'.format('security-advisor'),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_02_create_occurrence(self):
        """
        Test case for create_occurrence

        Creates a new `Occurrence`. Use this method to create `Occurrences` for a resource.
        """

        body = {
            "occurrence_id": "Occurrence01",
            "noteName": "projects/{}/notes/{}".format('security-advisor', 'Note01'),
            "short_description": "The short description of Occurrence01",
            "long_description": "The long description of Occurrence01"
        }

        response = self.client.open(
            path='/v1alpha1/projects/{}/occurrences'.format('security-advisor'),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_03_get_occurrence(self):
        """
        Test case for get_note

        Returns the requested `Note`.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}/occurrences/{}'.format('security-advisor', 'Occurrence01'),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_04_list_occurrences(self):
        """
        Test case for list_occurrences

        Lists active `Occurrences` for a given project matching the filters.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}/occurrences'.format('security-advisor'),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
        results = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(results), 1, "A array of one occurrence was expected.")

    def test_05_list_note_occurrences(self):
        """
        Test case for list_note_occurrences

        Lists `Occurrences` referencing the specified `Note`.
        Use this method to get all occurrences referencing your `Note` across all your customer projects.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}/notes/{}/occurrences'.format('security-advisor', 'Note01'),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })

        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
        results = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(results), 1, "An array of occurrence was expected.")

    def test_06_delete_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}/occurrences/{}'.format('security-advisor', 'Occurrence01'),
            method='DELETE',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_07_delete_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}/notes/{}'.format('security-advisor', 'Note01'),
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
