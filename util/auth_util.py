import jwt
import re


class Subject(object):
    def __init__(self, subject_id, subject_type, account_id):
        self.subject_id = subject_id
        self.subject_type = subject_type
        self.account_id = account_id

    def __str__(self):
        return "{}/{}/{}".format(self.subject_type, self.subject_id, self.account_id)


def get_subject(request):
    auth_header = request.headers['Authorization']
    if re.match('bearer', auth_header, re.I):
        auth_token = auth_header[7:]
    else:
        ValueError("Authorization header value does not start with 'bearer'")

    decoded_auth_token = jwt.decode(auth_token, verify=False)
    if 'iam_id' not in decoded_auth_token:
        ValueError("Invalid IAM bearer token")

    subject_id = decoded_auth_token['iam_id']
    subject_type = None

    if 'sub_type' not in decoded_auth_token:
        subject_type = 'user'
    else:
        sub_type = decoded_auth_token['sub_type']
        if sub_type == 'ServiceId':
            subject_type = 'service-id'
        elif sub_type == 'CRN':
            subject_type = 'crn'

    account = decoded_auth_token.get('account')
    if not account:
        ValueError("Missing 'account' field in IAM bearer token")

    account_id = account.get('bss')
    if not account_id:
        ValueError("Missing 'account.bss' field in IAM bearer token")

    subject = Subject(subject_id, subject_type, account_id)
    print("SUBJECT={}".format(subject))
    return subject
