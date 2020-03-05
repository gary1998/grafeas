# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
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

    def rest(self, **kwargs):
        if os.environ.get('AUTH_CLIENT_CLASS_NAME') == 'controllers.sa_auth.SecurityAdvisorAuthClient':
            kwargs["headers"]["X-Auth"] = os.environ['INTERNAL_SVC_TOKEN']
            kwargs["headers"]["X-UserToken"] = os.environ['X-UserToken']
        return self.client.open(**kwargs)

    def get_providers(self, account_id):
        return self.rest(
            path='/v1alpha1/{}/providers'.format(account_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def post_note(self, account_id, provider_id, body):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/notes'.format(
                account_id, provider_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def get_notes(self, account_id, provider_id):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/notes'.format(
                account_id, provider_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def get_note(self, account_id, provider_id, note_id):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/notes/{}'.format(
                account_id, provider_id, note_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def get_occurrence_note(self, account_id, provider_id, occurrence_id):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/occurrences/{}/note'.format(
                account_id, provider_id, occurrence_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def put_note(self, account_id, provider_id, note_id, body):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/notes/{}'.format(
                account_id, provider_id, note_id),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def delete_note(self, account_id, provider_id, note_id):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/notes/{}'.format(
                account_id, provider_id, note_id),
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def post_occurrence(self, account_id, provider_id, body):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/occurrences'.format(
                account_id, provider_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def post_or_put_occurrence(self, account_id, provider_id, body):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/occurrences'.format(
                account_id, provider_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN'],
                "Replace-If-Exists": "true"
            })

    def get_occurrences(self, account_id, provider_id):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/occurrences'.format(
                account_id, provider_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def get_occurrence(self, account_id, provider_id, occurrence_id):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/occurrences/{}'.format(
                account_id, provider_id, occurrence_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def get_note_occurrences(self, account_id, provider_id, note_id):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/notes/{}/occurrences'.format(
                account_id, provider_id, note_id),
            method='GET',
            headers={
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def put_occurrence(self, account_id, provider_id, occurrence_id, body):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/occurrences/{}'.format(
                account_id, provider_id, occurrence_id),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def delete_occurrence(self, account_id, provider_id, occurrence_id):
        return self.rest(
            path='/v1alpha1/{}/providers/{}/occurrences/{}'.format(
                account_id, provider_id, occurrence_id),
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })

    def delete_account_data(self, account_id):
        return self.rest(
            path='/v1alpha1/{}/data'.format(TEST_ACCOUNT_ID, account_id),
            method='DELETE',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth": os.environ['IAM_BEARER_TOKEN']
            })
