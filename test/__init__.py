from flask_testing import TestCase
import connexion
import json


class BaseTestCase(TestCase):
    def create_app(self):
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.add_api('swagger.yaml')
        return app.app

    def post_project(self, body):
        return self.client.open(
            path='/v1alpha1/projects',
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def get_projects(self):
        return self.client.open(
            path='/v1alpha1/projects',
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def get_project(self, project_id):
        return self.client.open(
            path='/v1alpha1/projects/{}'.format(project_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def delete_project(self, project_id):
        return self.client.open(
            path='/v1alpha1/projects/{}'.format(project_id),
            method='DELETE',
            headers={
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def post_note(self, project_id, body):
        return self.client.open(
            path='/v1alpha1/projects/{}/notes'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def get_notes(self, project_id):
        return self.client.open(
            path='/v1alpha1/projects/{}/notes'.format(project_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def get_note(self, project_id, note_id):
        return self.client.open(
            path='/v1alpha1/projects/{}/notes/{}'.format(project_id, note_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def get_occurrence_note(self, project_id, occurrence_id):
        return self.client.open(
            path = '/v1alpha1/projects/{}/occurrences/{}/notes'.format(project_id, occurrence_id),
            method = 'GET',
            headers = {
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def put_note(self, project_id, note_id, body):
        return self.client.open(
            path='/v1alpha1/projects/{}/notes/{}'.format(project_id, note_id),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def delete_note(self, project_id, note_id):
        return self.client.open(
            path='/v1alpha1/projects/{}/notes/{}'.format(project_id, note_id),
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def post_occurrence(self, project_id, body):
        return self.client.open(
            path='/v1alpha1/projects/{}/occurrences'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def post_or_put_occurrence(self, project_id, body):
        return self.client.open(
            path='/v1alpha1/projects/{}/occurrences'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX",
                "Replace-If-Exists": "true"
            })

    def get_occurrences(self, project_id):
        return self.client.open(
            path='/v1alpha1/projects/{}/occurrences'.format(project_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def get_occurrence(self, project_id, occurrence_id):
        return self.client.open(
            path='/v1alpha1/projects/{}/occurrences/{}'.format(project_id, occurrence_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def get_note_occurrences(self, project_id, note_id):
        return self.client.open(
            path='/v1alpha1/projects/{}/notes/{}/occurrences'.format(project_id, note_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def put_occurrence(self, project_id, occurrence_id, body):
        return self.client.open(
            path='/v1alpha1/projects/{}/occurrences/{}'.format(project_id, occurrence_id),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })

    def delete_occurrence(self, project_id, occurrence_id):
        return self.client.open(
            path='/v1alpha1/projects/{}/occurrences/{}'.format(project_id, occurrence_id),
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountX",
                "Authorization": "AuthorizationX"
            })
