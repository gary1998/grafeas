from flask import json
from http import HTTPStatus
import os
from .common_ut import BaseTestCase


FILE_NAMES = [
    "card_configured_data.json"
    #"mock_custom_data.json"
    #'mock_data_suspicious_servers.json',
    #'mock_data_suspicious_clients.json',
    #'mock_data_certificates.json',
    #'mock_data_containers_with_vulnerabilities.json',
    #'mock_data_images_with_vulnerabilities.json'
]


class RemoveMockData(BaseTestCase):
    def test_01_remove_notes(self):
        for file_name in FILE_NAMES:
            with open("test/data/{}".format(file_name)) as f:
                data = json.load(f)
                for note in data.get('notes', []):
                    self._remove_note(note['project_id'], note)

    def test_02_remove_occurrences(self):
        for file_name in FILE_NAMES:
            with open("test/data/{}".format(file_name)) as f:
                data = json.load(f)
                for occurrence in data.get('occurrences', []):
                    self._remove_occurrence(occurrence['project_id'], occurrence)

    def _remove_note(self, project_id, body):
        response = self._delete('/v1alpha1/projects/{}/notes/{}'.format(project_id, body['id']))
        self.assertTrue(response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND],
                        "Response body is : " + response.data.decode('utf-8'))

    def _remove_occurrence(self, project_id, body):
        response = self._delete('/v1alpha1/projects/{}/occurrences/{}'.format(project_id, body['id']))
        self.assertTrue(response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND],
                        "Response body is : " + response.data.decode('utf-8'))

    def _delete(self, path):
        return self.client.open(
            path=path,
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            }
        )
