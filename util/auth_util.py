import json
import logging
from util import rest_client


logger = logging.getLogger("grafeas.auth_util")


class Subject(object):
    def __init__(self, id, type_, account_id):
        self.id = id
        self.type = type_
        self.account_id = account_id

    def __str__(self):
        return "type={}, id={}, account={}".format(self.type, self.id, self.account_id)


def get_subject(decoded_auth_token):
    iam_id = decoded_auth_token.get('iam_id')
    if iam_id is None:
        raise ValueError("Invalid IAM token: missing 'iam_id' field")

    if 'sub_type' not in decoded_auth_token:
        type_ = 'user'
    else:
        sub_type = decoded_auth_token['sub_type']
        if sub_type == 'ServiceId':
            type_ = 'service-id'
        else:
            raise ValueError("Invalid IAM token: unsupported '{}' subject type".format(sub_type))

    account = decoded_auth_token.get('account')
    if not account:
        raise ValueError("Invalid IAM token: missing 'account' field")

    account_id = account.get('bss')
    if not account_id:
        raise ValueError("Invalid IAM token: missing 'account.bss' field")

    return Subject(iam_id, type_, account_id)


def get_identity_token(iam_base_url, api_key):
    with rest_client.RestClient() as client:
        client.add_header("Accept", "application/json")
        client.add_header("Content-Type", "application/x-www-form-urlencoded")

        body = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        }

        response = client.post(
            url="{}/identity/token".format(iam_base_url),
            data=body)

        if response.status_code != 200:
            response.raise_for_status()

        content = json.loads(response.content.decode('utf-8'))
        return content['access_token']
