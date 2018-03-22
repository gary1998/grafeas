from flask import json
from http import HTTPStatus
from .common_ut import BaseTestCase


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
            "finding": {
                "severity": "HIGH"
            },
            "reported_by": {
                "id": "The reporter ID",
                "title": "The reporter title",
                "url": "The reporter URL"
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
            "finding": {
                "severity": "MEDIUM"
            },
            "reported_by": {
                "id": "The reporter ID",
                "title": "The reporter title",
                "url": "The reporter URL"
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
                "account_id": "0209df6649c995e076657f797cb8b6fb"
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
                "account_id": "0209df6649c995e076657f797cb8b6fb"
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
                "account_id": "0209df6649c995e076657f797cb8b6fb"
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
        self.assertTrue(len(results) > 0, "An array of one ore more occurrences was expected.")

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

    def test_09_create_invalid_occurrence(self):

        body = {
            "context":{
                "region":"dal10",
                "account_id": "697e84fcca45c9439aae525d31ef1a27",
                "resource_name": "N1",
                "resource_type": "Pod",
                "service_crn":"39438df3496a49e8aa39eb556ab15b0e",
                "service_name":"Kubernetes Cluster"
             },
            "finding":{
                "certainty":"LOW",
                "network":{
                    "client":{"ip":"1.2.3.1"},
                    "direction":"Outbound",
                    "protocol":	"ALL_METHODS"
                }
            }
        }

        response = self.post_occurrence('ProjectX', body)
        self.assertStatus(response, HTTPStatus.BAD_REQUEST, "Response body is : " + response.data.decode('utf-8'))

    def test_10_delete_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """

        response = self.delete_occurrence('ProjectX', 'Occurrence02')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_11_delete_missing_occurrence(self):
        """
        Test case for delete_occurrence

        Deletes the given `Occurrence` from the system.
        """

        response = self.delete_occurrence('ProjectX', 'Occurrence02')
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))

    def test_12_delete_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """

        response = self.delete_note('ProjectX', 'Note02')
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_13_delete_missing_note(self):
        """
        Test case for delete_note

        Deletes the given `Note` from the system.
        """

        response = self.delete_note('ProjectX', 'Note02')
        self.assertStatus(response, HTTPStatus.NOT_FOUND, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
