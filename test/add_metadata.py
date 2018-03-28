from flask import json
from http import HTTPStatus
import os
from .common_ut import BaseTestCase


FILE_NAMES = [
    "sa-sections.json",
    "notes-certificates.json",
    "notes-images_with_vulnerabilities.json",
    "notes-suspicious_clients.json",
    "notes-suspicious_servers.json"
]


class AddMetadaData(BaseTestCase):
    def test_01_create_projects(self):
        for file_name in FILE_NAMES:
            with open("metadata/{}".format(file_name)) as f:
                data = json.load(f)
                for project in data.get('projects', []):
                    self._add_project(project)

    def test_02_create_notes(self):
        for file_name in FILE_NAMES:
            with open("metadata/{}".format(file_name)) as f:
                data = json.load(f)
                for note in data.get('notes', []):
                    self._add_note(note['project_id'], note)

    def _add_project(self, body):
        response = self.client.open(
            path='/v1alpha1/projects',
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })
        self.assertTrue(response.status_code in [HTTPStatus.OK, HTTPStatus.CONFLICT],
                        "Response body is : " + response.data.decode('utf-8'))

    def _add_note(self, project_id, body):
        response = self._create_or_replace(
            '/v1alpha1/projects/{}/notes'.format(project_id),
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
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })
        if response.status_code == HTTPStatus.CONFLICT:
            response = self.client.open(
                path="{}/{}".format(path, body['id']),
                method='PUT',
                data=json.dumps(body),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": os.environ['IAM_BEARER_TOKEN']
                })

        return response
