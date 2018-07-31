import json
import os
from util import rest_client
from requests import HTTPError


class CommonFVT(object):
    def __init__(self, api_base_url):
        self.client = rest_client.RestClient()
        self.client.add_header("Accept", "application/json")
        self.client.add_bearer_auth_header(os.environ['IAM_BEARER_TOKEN'])
        self.api_base_url = api_base_url

    def assert_status(self, response, status_code):
        if response is None:
            print("FAILURE - Exception raised (no response)")
            return

        if response.status_code == status_code:
            print("OK: {}".format(response.content.decode('utf-8')))
        else:
            print("FAILURE: {}".format(response.content.decode('utf-8')))

        print("Request Headers: {}".format(response.request.headers))
        print("Response Headers: {}".format(response.headers))

    def assert_true(self, value, message):
            if value:
                print("OK")
            else:
                print("FAILURE: {}".format(message))

    def post(self, url, data, headers=None):
        try:
            return self.client.post(url, data, headers, verify=False)
        except HTTPError as e:
            print(e)
            return None

    def get(self, url, headers=None):
        try:
            return self.client.get(url, headers, verify=False)
        except HTTPError as e:
            print(e)
            return None

    def put(self, url, data, headers=None):
        try:
            return self.client.put(url, data, headers, verify=False)
        except HTTPError as e:
            print(e)
            return None

    def delete(self, url, headers=None):
        try:
            return self.client.delete(url, headers, verify=False)
        except HTTPError as e:
            print(e)
            return None

    def get_providers(self):
        return self.get(
            url='{}/v1alpha1/providers'.format(
                self.api_base_url))

    def post_note(self, provider_id, body):
        return self.post(
            url='{}/v1alpha1/providers/{}/notes'.format(
                self.api_base_url, provider_id),
            data=json.dumps(body),
            headers={"Content-Type": "application/json"})

    def get_notes(self, provider_id):
        return self.get(
            url='{}/v1alpha1/providers/{}/notes'.format(
                self.api_base_url, provider_id))

    def get_note(self, provider_id, note_id):
        return self.get(
            url='{}/v1alpha1/providers/{}/notes/{}'.format(
                self.api_base_url, provider_id, note_id))

    def get_occurrence_note(self, provider_id, occurrence_id):
        return self.get(
            url = '{}/v1alpha1/providers/{}/occurrences/{}/note'.format(
                self.api_base_url, provider_id, occurrence_id))

    def put_note(self, provider_id, note_id, body):
        return self.put(
            url='{}/v1alpha1/providers/{}/notes/{}'.format(
                self.api_base_url, provider_id, note_id),
            data=json.dumps(body),
            headers={"Content-Type": "application/json"})

    def delete_note(self, provider_id, note_id):
        return self.delete(
            url='{}/v1alpha1/providers/{}/notes/{}'.format(
                self.api_base_url, provider_id, note_id))

    def post_occurrence(self, provider_id, body):
        return self.post(
            url='{}/v1alpha1/providers/{}/occurrences'.format(
                self.api_base_url, provider_id),
            data=json.dumps(body),
            headers={"Content-Type": "application/json"})

    def post_or_put_occurrence(self, provider_id, body):
        return self.post(
            url='{}/v1alpha1/providers/{}/occurrences'.format(
                self.api_base_url, provider_id),
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Replace-If-Exists": "true"
            })

    def get_occurrences(self, provider_id):
        return self.get(
            url='{}/v1alpha1/providers/{}/occurrences'.format(
                self.api_base_url, provider_id))

    def get_occurrence(self, provider_id, occurrence_id):
        return self.client.get(
            url='{}/v1alpha1/providers/{}/occurrences/{}'.format(
                self.api_base_url, provider_id, occurrence_id))

    def get_note_occurrences(self, provider_id, note_id):
        return self.get(
            url='{}/v1alpha1/providers/{}/notes/{}/occurrences'.format(
                self.api_base_url, provider_id, note_id))

    def put_occurrence(self, provider_id, occurrence_id, body):
        return self.put(
            url='{}/v1alpha1/providers/{}/occurrences/{}'.format(
                self.api_base_url, provider_id, occurrence_id),
            data=json.dumps(body),
            headers={"Content-Type": "application/json"})

    def delete_occurrence(self, provider_id, occurrence_id):
        return self.delete(
            url='{}/v1alpha1/providers/{}/occurrences/{}'.format(
                self.api_base_url, provider_id, occurrence_id))