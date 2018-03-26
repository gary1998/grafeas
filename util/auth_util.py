import json
import jwt
import logging
import os
import re
import threading
from flask import request
from util import qradar_client
from util import rest_client


logger = logging.getLogger("grafeas.auth_util")


class Subject(object):
    def __init__(self, id, type_, account_id):
        self.id = id
        self.type = type_
        self.account_id = account_id

    def __str__(self):
        return "type={}, id={}, account={}".format(self.type, self.id, self.account_id)


def get_subject(request):
    try:
        id_ = None
        if not validate_proto(request):
            raise ValueError("Only HTTPS connections are allowed")

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

        id_ = decoded_auth_token['iam_id']

        if 'sub_type' not in decoded_auth_token:
            type_ = 'user'
        else:
            sub_type = decoded_auth_token['sub_type']
            if sub_type == 'ServiceId':
                type_ = 'service-id'
            else:
                raise ValueError("Unsupported subject type: {}".format(sub_type))

        account = decoded_auth_token.get('account')
        if not account:
            raise ValueError("Invalid IAM token")

        account_id = account.get('bss')
        if not account_id:
            raise ValueError("Invalid IAM token")

        return Subject(id_, type_, account_id)
    except:
        _log_web_service_auth_failed(id_ if id_ else "NO-NAME")
        raise


def validate_proto(request):
    accept_http = os.environ.get('ACCEPT_HTTP', "false")
    if accept_http.lower() == 'true':
        return True

    x_forwarded_proto = request.headers.get("X-Forwarded-Proto")
    if x_forwarded_proto:
        proto = x_forwarded_proto.strip()
        if proto == 'https':
            return True

    return False


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


#
# QRADAR
#

QRADAR_APP_ID = "ng.bluemix.net"
QRADAR_COMP_ID = "legato"
QRADAR_PRIVATE_KEY_FILE = "qr_k"
QRADAR_CERT_FILE = "qr_c"
QRADAR_CA_CERTS_FILE = "qr_cac"


__qradar_client = None
__qradar_client_lock = threading.Lock()


def get_qradar_client():
    """
    Opens a new db connection if there is none yet for the current application context.
    """

    global __qradar_client
    with __qradar_client_lock:
        if __qradar_client is None:
            __qradar_client = _init_qradar_client()
        return __qradar_client


def _init_qradar_client():
    if 'QRADAR_HOST' not in os.environ:
        logger.warning("QRadar logging is not enabled due to missing environment variable %s", "QRADAR_HOST")
        return None

    config_dir = os.environ.get('CONFIG', "config")
    return qradar_client.QRadarClient(
        os.environ['QRADAR_HOST'],
        int(os.environ.get('QRADAR_PORT', "6515")),
        QRADAR_APP_ID, QRADAR_COMP_ID,
        qradar_client.QRadarClient.LOG_USER,
        os.path.join(config_dir, QRADAR_PRIVATE_KEY_FILE),
        os.path.join(config_dir, QRADAR_CERT_FILE),
        os.path.join(config_dir, QRADAR_CA_CERTS_FILE))


def _log_web_service_auth_succeeded(user_name):
    qradar_client = get_qradar_client()
    try:
        if qradar_client is not None:
            method, url, source_addr, source_port, dest_addr, dest_port = _get_request_info()
            qradar_client.log_web_service_auth_succeeded(
                method, url, user_name,
                source_addr, source_port,
                dest_addr, dest_port)
    except:
        # QRadar is not available, skip this
        logger.exception("Unexpected error while sending 'web service auth succeeded' record to QRadar")


def _log_web_service_auth_failed(user_name):
    qradar_client = get_qradar_client()
    if qradar_client is not None:
        try:
            method, url, source_addr, source_port, dest_addr, dest_port = _get_request_info()
            qradar_client.log_web_service_auth_failed(
                method, url, user_name,
                source_addr, source_port,
                dest_addr, dest_port)
        except:
            # QRadar is not available, skip this
            logger.exception("Unexpected error while sending 'web service auth failed' record to QRadar")


def _get_request_info():
    env = request.environ
    method = env['REQUEST_METHOD']
    url = request.url
    source_addr, source_port = _get_request_source()
    host_n_port = env['HTTP_HOST'].split(':')
    dest_addr = host_n_port[0]
    dest_port = host_n_port[1] if len(host_n_port) == 2 else "80"
    return method, url, source_addr, source_port, dest_addr, dest_port


def _get_request_source():
    env = request.environ
    headers = request.headers

    if headers.getlist("X-Forwarded-For"):
        forwarded_for = request.headers.getlist("X-Forwarded-For")[0]
        source_addrs = forwarded_for.split(',')
        source_addr = source_addrs[0].strip()
    else:
        source_addr = env['REMOTE_ADDR']

    if headers.getlist("X-Forwarded-Port"):
        forwarded_port = request.headers.get("X-Forwarded-Port")
        source_port = forwarded_port.strip()
    else:
        source_port = env['REMOTE_PORT']

    return source_addr, source_port

