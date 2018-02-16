import jwt
import re


def get_account_id(request):
    #TODO: Temporary workaround until IAM token are not passed in the Authorization header
    if 'Account' in request.headers:
        account_id = request.headers['Account']
        return account_id

    auth_header = request.headers['Authorization']
    if re.match('bearer', auth_header, re.I):
        auth_token = auth_header[7:]
    else:
        ValueError("Authorization header value does not start with 'bearer'")

    decoded_auth_token = jwt.decode(auth_token, verify=False)
    client_id = decoded_auth_token.get('client_id')
    if client_id is None:
        ValueError("Missing client id in bearer token")

    if client_id != 'bx':
        if client_id == 'cf':
            raise ValueError("Support for 'cf' client id coming soon!")
        else:
            raise ValueError("Unsupported client id: {}", client_id)

    account = decoded_auth_token.get('account')
    if account is None:
        ValueError("Missing 'account' field in IAM bearer token")

    if account is  None:
        ValueError("Missing 'account.bss' field in IAM bearer token")

    account_id = account['bss']
    return account_id
