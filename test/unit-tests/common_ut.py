from flask_testing import TestCase
import connexion
import json
import os
from controllers import auth

TEST_ACCOUNT_ID = os.environ['TEST_ACCOUNT_ID']


class BaseTestCase(TestCase):
    def create_app(self):
        app = connexion.App(__name__, specification_dir='../../swagger/')
        app.add_api('swagger.yaml')
        app.app.config['TESTING'] = True
        return app.app

    @classmethod
    def tearDownClass(cls):
        auth.close_auth_client()

    def post_project(self, body):
        return self.client.open(
            path='/v1alpha1/{}/projects'.format(TEST_ACCOUNT_ID),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def get_projects(self):
        return self.client.open(
            path='/v1alpha1/{}/projects'.format(TEST_ACCOUNT_ID),
            method='GET',
            headers={
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def get_project(self, project_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}'.format(TEST_ACCOUNT_ID, project_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def delete_project(self, project_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}'.format(TEST_ACCOUNT_ID, project_id),
            method='DELETE',
            headers={
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def post_note(self, project_id, body):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/notes'.format(TEST_ACCOUNT_ID, project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def get_notes(self, project_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/notes'.format(TEST_ACCOUNT_ID, project_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def get_note(self, project_id, note_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/notes/{}'.format(TEST_ACCOUNT_ID, project_id, note_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def get_occurrence_note(self, project_id, occurrence_id):
        return self.client.open(
            path = '/v1alpha1/{}/projects/{}/occurrences/{}/note'.format(TEST_ACCOUNT_ID, project_id, occurrence_id),
            method = 'GET',
            headers = {
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def put_note(self, project_id, note_id, body):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/notes/{}'.format(TEST_ACCOUNT_ID, project_id, note_id),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def delete_note(self, project_id, note_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/notes/{}'.format(TEST_ACCOUNT_ID, project_id, note_id),
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def post_occurrence(self, project_id, body):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/occurrences'.format(TEST_ACCOUNT_ID, project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def post_or_put_occurrence(self, project_id, body):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/occurrences'.format(TEST_ACCOUNT_ID, project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN'],
                "Replace-If-Exists": "true"
            })

    def get_occurrences(self, project_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/occurrences'.format(TEST_ACCOUNT_ID, project_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def get_occurrence(self, project_id, occurrence_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/occurrences/{}'.format(TEST_ACCOUNT_ID, project_id, occurrence_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def get_note_occurrences(self, project_id, note_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/notes/{}/occurrences'.format(TEST_ACCOUNT_ID, project_id, note_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def put_occurrence(self, project_id, occurrence_id, body):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/occurrences/{}'.format(TEST_ACCOUNT_ID, project_id, occurrence_id),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def delete_occurrence(self, project_id, occurrence_id):
        return self.client.open(
            path='/v1alpha1/{}/projects/{}/occurrences/{}'.format(TEST_ACCOUNT_ID, project_id, occurrence_id),
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })

    def delete_account_data(self, account_id):
        return self.client.open(
            path='/v1alpha1/{}/accounts/{}'.format(TEST_ACCOUNT_ID, account_id),
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": os.environ['IAM_BEARER_TOKEN']
            })
