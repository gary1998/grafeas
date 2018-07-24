# set environment variable
import os
import logging
import sys
import jwt
from util.auth_util import get_identity_token

import json
import base64

os.environ["vault_url"] = "https://vserv-us.sos.ibm.com:8200"
os.environ["vault_path"] = "v1/generic/crn/v1/dev/public/security-advisor/us-south/YS1/-/-/-"

# os.environ["vault_role_id"] = ""
# os.environ["vault_secret_id"] = ""

if os.environ.get('vault_role_id') and os.environ.get('vault_secret_id'):
    import inflection
    import pyvault

    def constant_case(secrets):
        for vault_key, vault_key_pair_value in secrets.items():
            for k, v in vault_key_pair_value.items():
                # if key in vault is cloudant_url make it CLOUDANT_URL , iamConfig becomes IAM_CONFIG
                constant_case_env_var = inflection.underscore(k).upper()
                os.environ[inflection.underscore(
                    k).upper()] = base64.b64decode(v).decode('utf-8')

    pyvault.load_vault_secrets_in_environment(
        keys=["cloudant-credentials", "grafeas-secret"], env_loader_func=constant_case)
else:
    logging.warn("vault_role_id and vault_secret_id are not set")

if os.environ.get("CLOUDANT_URL_NO_CREDS"):
    os.environ["CLOUDANT_URL"] = os.environ["CLOUDANT_URL_NO_CREDS"]

if not os.environ.get('ACCEPT_HTTP'):
    logging.warn("ACCEPT_HTTP is not set, setting it to true")
    os.environ['ACCEPT_HTTP'] = "true"

if not os.environ.get('GRAFEAS_DB_NAME'):
    logging.warn("GRAFEAS_DB_NAME is not set, setting it to grafeas")
    os.environ['GRAFEAS_DB_NAME'] = "grafeas"


if not os.environ.get('IAM_BEARER_TOKEN'):

    iam_base_url = os.environ.get('IAM_BASE_URL') \
        or 'https://iam.stage1.bluemix.net'

    iam_config = os.environ.get("IAM_CONFIG")
    if iam_config:
        os.environ["IAM_API_KEY"] = json.loads(
            iam_config)["viewerService"]["apiKey"]

    if not os.environ.get("IAM_API_KEY"):
        logging.error(
            "IAM_API_KEY which holds the operator key for pdp is missing")
        sys.exit(1)

    test_iam_api_key = os.environ.get('GRAFEAS_TEST_IAM_API_KEY')

    if not test_iam_api_key:
        logging.error(
            'IAM_BEARER_TOKEN must be specified, else GRAFEAS_TEST_IAM_API_KEY should be provided. Default value of IAM_BASE_URL is https://iam.stage1.ng.bluemix.net')
        sys.exit(1)
    else:
        access_token = get_identity_token(iam_base_url, test_iam_api_key)
        os.environ['IAM_BEARER_TOKEN'] = '{} {}'.format(
            'Bearer', access_token)


if not os.environ.get('TEST_ACCOUNT_ID'):
    decoded_auth_token = jwt.decode(
        os.environ['IAM_BEARER_TOKEN'][7:], verify=False)
    os.environ['TEST_ACCOUNT_ID'] = decoded_auth_token['account']['bss']


if not os.environ.get('AUTH_CLIENT_CLASS_NAME'):
    logging.warn(
        "AUTH_CLIENT_CLASS_NAME is not set, setting it to controllers.sa_auth.SecurityAdvisorAuthClient")
    os.environ['AUTH_CLIENT_CLASS_NAME'] = "controllers.sa_auth.SecurityAdvisorAuthClient"

if os.environ.get('AUTH_CLIENT_CLASS_NAME') == "controllers.sa_auth.SecurityAdvisorAuthClient":
    import json
    internal_svc_api_key = json.loads(os.environ.get('IAM_CONFIG'))[
        "internalService"]["apiKey"]
    access_token = get_identity_token(iam_base_url, internal_svc_api_key)
    os.environ['INTERNAL_SVC_TOKEN'] = '{} {}'.format('Bearer', access_token)
    os.environ['X-UserToken'] = os.environ['IAM_BEARER_TOKEN']
    decoded = jwt.decode(os.environ['X-UserToken'][7:], verify=False)
    user_account = decoded['account']['bss']
    user_id = decoded['iam_id']
    os.environ['WHITELISTED_ENTITY'] = '[{"id": "%s", "account": "%s" }]' % (
        user_id, user_account)
    logging.warn(os.environ['WHITELISTED_ENTITY'])


if os.environ.get("TEST_ENVIRONEMT", "stage") == "stage":
    os.environ["IAM_TOKEN_VALIDATION_URL"] = "https://iam.stage1.bluemix.net/identity/keys"
    os.environ["IAM_TOKEN_URL"] = "https://iam.stage1.bluemix.net/identity/token"
    os.environ["IAM_PDP_URL"] = "https://iam.stage1.bluemix.net"
    os.environ["IAM_PAP_URL"] = "https://iam.stage1.bluemix.net"
