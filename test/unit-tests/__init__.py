# set environment variable
import os
import logging
import requests
import sys

if not os.environ.get('ACCEPT_HTTP'):
  logging.warn("ACCEPT_HTTP is not set, setting it to true")
  os.environ['ACCEPT_HTTP'] = "true"

if not os.environ.get('GRAFEAS_DB_NAME'):
  logging.warn("GRAFEAS_DB_NAME is not set, setting it to grafeas")
  os.environ['GRAFEAS_DB_NAME'] = "grafeas"


def generate_access_token(url, api_key):

    response = requests.post(url,
                             data={'grant_type': 'urn:ibm:params:oauth:grant-type:apikey'
                             , 'apikey': api_key},
                             headers={'Accept': 'application/json',
                             'Authorization': 'Basic Yng6Yng=',
                             'Content-Type': 'application/x-www-form-urlencoded'
                             })

    return response.json()['access_token']


if not os.environ.get('IAM_BEARER_TOKEN'):

    # generate one using GRAFEAS_TEST_IAM_API_KEY

    iam_base_url = os.environ.get('IAM_BASE_URL') \
        or 'http://iam.ng.bluemix.net'
    token_url = '{}/identity/token'.format(iam_base_url)
    logging.info('IAM token url is %s', token_url)

    iam_api_key = os.environ.get('GRAFEAS_TEST_IAM_API_KEY')
    if not iam_api_key:
        logging.error('IAM_BEARER_TOKEN must be specified, else GRAFEAS_TEST_IAM_API_KEY should be provided. Default value of IAM_BASE_URL is http://iam.ng.bluemix.net')
        sys.exit(1)
    else:
        access_token = generate_access_token(token_url, iam_api_key)
        os.environ['IAM_BEARER_TOKEN'] = '{} {}'.format('Bearer',access_token)
