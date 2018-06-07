# set environment variable
import os
import logging
import requests
import sys
from util.auth_util import get_identity_token

if not os.environ.get('ACCEPT_HTTP'):
  logging.warn("ACCEPT_HTTP is not set, setting it to true")
  os.environ['ACCEPT_HTTP'] = "true"

if not os.environ.get('GRAFEAS_DB_NAME'):
  logging.warn("GRAFEAS_DB_NAME is not set, setting it to grafeas")
  os.environ['GRAFEAS_DB_NAME'] = "grafeas"


if not os.environ.get('IAM_BEARER_TOKEN'):

    # generate one using GRAFEAS_TEST_IAM_API_KEY

    iam_base_url = os.environ.get('IAM_BASE_URL') \
        or 'http://iam.ng.bluemix.net'

    iam_api_key = os.environ.get('GRAFEAS_TEST_IAM_API_KEY')
    if not iam_api_key:
        logging.error('IAM_BEARER_TOKEN must be specified, else GRAFEAS_TEST_IAM_API_KEY should be provided. Default value of IAM_BASE_URL is http://iam.ng.bluemix.net')
        sys.exit(1)
    else:
        access_token = get_identity_token(iam_base_url, iam_api_key)
        os.environ['IAM_BEARER_TOKEN'] = '{} {}'.format('Bearer',access_token)