from . import BaseTestCase
from flask import json


class TestMockData(BaseTestCase):
    def test_01_create_projects(self):
        with open("test/data/mock_data.json") as f:
            data = json.load(f)
            for project in data['projects']:
                self.post_project(project)

    def test_02_create_notes(self):
        with open("test/data/mock_data.json") as f:
            data = json.load(f)
            for note in data['notes']:
                self.post_note(note['project_id'], note)

    def test_03_create_occurrences(self):
        with open("test/data/mock_data.json") as f:
            data = json.load(f)
            for occurrence in data['occurrences']:
                self.post_occurrence(occurrence['project_id'], occurrence)

    def post_project(self, body):
        response = self.client.open(
            path='/v1alpha1/projects',
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def post_note(self, project_id, body):
        response = self.client.open(
            path='/v1alpha1/projects/{}/notes'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def post_occurrence(self, project_id, body):
        response = self.client.open(
            path='/v1alpha1/projects/{}/occurrences'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))