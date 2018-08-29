# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
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
    def test_01_create_notes(self):
        for file_name in FILE_NAMES:
            with open("metadata/{}".format(file_name)) as f:
                data = json.load(f)
                for note in data.get('notes', []):
                    self._add_note(note['provider_id'], note)

    def _add_note(self, provider_id, body):
        response = self._create_or_replace(
            '/v1alpha1/providers/{}/notes'.format(provider_id),
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
