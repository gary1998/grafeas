from . import BaseTestCase
from flask import json
from http import HTTPStatus


FILE_NAMES = [
    # 'mock_data_suspicious_servers.json',
    # 'mock_data_suspicious_clients.json',
    # 'mock_data_certificates.json',
    'mock_data_containers_with_vulnerabilities.json',
    'mock_data_images_with_vulnerabilities.json'
]


class TestMockData(BaseTestCase):
    def test_01_create_projects(self):
        for file_name in FILE_NAMES:
            with open("test/data/{}".format(file_name)) as f:
                data = json.load(f)
                for project in data.get('projects', []):
                    self._add_project(project)

    def test_02_create_notes(self):
        for file_name in FILE_NAMES:
            with open("test/data/{}".format(file_name)) as f:
                data = json.load(f)
                for note in data.get('notes', []):
                    self._add_note(note['project_id'], note)

    def test_03_create_occurrences(self):
        for file_name in FILE_NAMES:
            with open("test/data/{}".format(file_name)) as f:
                data = json.load(f)
                for occurrence in data.get('occurrences', []):
                    self._add_occurrence(occurrence['project_id'], occurrence)

    def _add_project(self, body):
        response = self.client.open(
            path='/v1alpha1/projects',
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "d0c8a917589e40076961f56b23056d16",
                "Authorization": "Authorization01"
            })
        self.assertTrue(response.status_code in [HTTPStatus.OK, HTTPStatus.CONFLICT],
                        "Response body is : " + response.data.decode('utf-8'))

    def _add_note(self, project_id, body):
        response = self._create_or_replace(
            '/v1alpha1/projects/{}/notes'.format(project_id),
            body)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def _add_occurrence(self, project_id, body):
        response = self._create_or_replace(
            '/v1alpha1/projects/{}/occurrences'.format(project_id),
            body)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def _create_or_replace(self, path, body):
        response = self.client.open(
            path=path,
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "d0c8a917589e40076961f56b23056d16",
                "Authorization": "Authorization01"
            })
        if response.status_code == HTTPStatus.CONFLICT:
            response = self.client.open(
                path="{}/{}".format(path, body['id']),
                method='PUT',
                data=json.dumps(body),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Account": "d0c8a917589e40076961f56b23056d16",
                    "Authorization": "Authorization01"
                })

        return response
