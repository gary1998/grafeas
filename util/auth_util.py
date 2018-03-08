import json
import jwt
import re
from util import rest_client


class Subject(object):
    def __init__(self, subject_id, subject_type, account_id):
        self.subject_id = subject_id
        self.subject_type = subject_type
        self.account_id = account_id

    def __str__(self):
        return "type={}, id={}, account={}".format(self.subject_type, self.subject_id, self.account_id)


def get_subject(request):
    auth_header = request.headers['Authorization']
    if re.match('bearer ', auth_header, re.I):
        auth_token = auth_header[7:]
    else:
        auth_token = auth_header

    try:
        decoded_auth_token = jwt.decode(auth_token, verify=False)
    except jwt.DecodeError:
        raise ValueError("Invalid JWT token")

    if 'iam_id' not in decoded_auth_token:
        raise ValueError("Invalid IAM token")

    subject_id = decoded_auth_token['iam_id']

    if 'sub_type' not in decoded_auth_token:
        subject_type = 'user'
    else:
        sub_type = decoded_auth_token['sub_type']
        if sub_type == 'ServiceId':
            subject_type = 'service-id'
        else:
            raise ValueError("Unsupported subject type: {}".format(sub_type))

    account = decoded_auth_token.get('account')
    if not account:
        raise ValueError("Invalid IAM token")

    account_id = account.get('bss')
    if not account_id:
        raise ValueError("Invalid IAM token")

    return Subject(subject_id, subject_type, account_id)


def get_identity_token(iam_base_url, api_key):
    client = rest_client.RestClient()
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
