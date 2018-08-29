# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import json
import logging
from util import rest_client


logger = logging.getLogger("grafeas.auth_util")


class Subject(object):
    def __init__(self, kind, id, account_id, email=None):
        self.kind = kind
        self.id = id
        self.account_id = account_id
        self.email = email

    def __str__(self):
        return "{{kind:{}, id:{}, account:{}, email:{}}}".format(self.kind, self.id, self.account_id, self.email)

    def to_dict(self):
        return {
            'kind': self.kind,
            'id': self.id,
            'account_id': self.account_id,
            'email': self.email
        }


def get_subject(decoded_auth_token):
    if 'sub_type' not in decoded_auth_token:
        kind = 'user'
    else:
        sub_type = decoded_auth_token['sub_type']
        if sub_type == 'ServiceId':
            kind = 'service-id'
        else:
            raise ValueError("Invalid IAM token: unsupported '{}' subject type".format(sub_type))

    iam_id = decoded_auth_token.get('iam_id')
    if iam_id is None:
        raise ValueError("Invalid IAM token: missing 'iam_id' field")

    account = decoded_auth_token.get('account')
    if not account:
        raise ValueError("Invalid IAM token: missing 'account' field")

    account_id = account.get('bss')
    if not account_id:
        raise ValueError("Invalid IAM token: missing 'account.bss' field")

    email = decoded_auth_token.get('email')
    # email could be missing. For example, in subjects of 'service-id' kind

    return Subject(kind, iam_id, account_id, email)


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
