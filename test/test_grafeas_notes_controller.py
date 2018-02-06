# coding: utf-8

from . import BaseTestCase
from flask import json


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

    def test_02_get_note(self):
        """
        Test case for get_note

        Returns the requested `Note`.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}/notes/{}'.format('security-advisor', 'Note01'),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_03_list_notes(self):
        """
        Test case for list_notes

        Lists all `Notes` for a given project.
        """

        response = self.client.open(
            path='/v1alpha1/projects/{}/notes'.format('security-advisor'),
            method='GET',
            content_type='application/json',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
        results = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(results), 1, "An array of one note was expected.")

    def test_04_create_occurrence(self):
        """
        Test case for create_occurrece

        Returns the requested `Note`.
        """

        body = {
            "id": "Occurrence01",
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

    def test_05_get_occurrence_note(self):
        """
        Test case for get_occurrence_note

        Gets the `Note` attached to the given `Occurrence`.
        """
        response = self.client.open(
            path='/v1alpha1/projects/{}/occurrences/{}/notes'.format('security-advisor', 'Occurrence01'),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_06_update_note(self):
        """
        Test case for update_note

        Updates an existing `Note`.
        """

        body = {
            "short_description": "The updated short description of Note01",
            "long_description": "The updated long description of Note01"
        }

        response = self.client.open(
            path='/v1alpha1/projects/{}/notes/{}'.format('security-advisor', 'Note01'),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    '''
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

    def test_08_delete_occurrence(self):
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
    '''

if __name__ == '__main__':
    import unittest
    unittest.main()
