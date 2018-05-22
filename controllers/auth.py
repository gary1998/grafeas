import jwt
import logging
import os
import re
import threading
import pepclient
from util import auth_util
from util import exceptions
from util import qradar_client


logger = logging.getLogger("grafeas.auth")

#
# QRADAR
#

QRADAR_APP_ID = "ng.bluemix.net"
QRADAR_COMP_ID = "legato"
QRADAR_PRIVATE_KEY_FILE = "qr_k"
QRADAR_CERT_FILE = "qr_c"
QRADAR_CA_CERTS_FILE = "qr_cac"


#
# PEP Client initialization and access
#

class GrafeasAuthClient(object):
    def __init__(self, enabled=True):
        logger.info("Initializing auth client ...")
        self.iam_base_url = os.environ['IAM_BASE_URL']
        self.iam_api_base_url = os.environ['IAM_API_BASE_URL']
        self.api_key = os.environ['IAM_API_KEY']
        self.access_token = auth_util.get_identity_token(self.iam_base_url, self.api_key)
        self.pep_client = pepclient.PEPClient(xacml_url=self.iam_api_base_url, auth_token=self.access_token)
        self.token_client = pepclient.TokenClient(iam_endpoint=self.iam_api_base_url)
        self.qradar_client = GrafeasAuthClient._init_qradar_client()
        self.enabled = enabled
        logger.info("Auth client initialized.")

    def close(self):
        try:
            self.pep_client.finish()
        except:
            logger.exception("An unexpected error was encountered while closing PEP client")
        try:
            self.qradar_client.close()
        except:
            logger.exception("An unexpected error was encountered while closing QRadar client")

    def enable(self, value):
        self.enabled = value

    def get_subject(self, request):
        if not GrafeasAuthClient.validate_proto(request):
            raise exceptions.UnauthorizedError("Only HTTPS connections are allowed")

        try:
            auth_header = request.headers['Authorization']
            if re.match('bearer ', auth_header, re.I):
                auth_token = auth_header[7:]
            else:
                auth_token = auth_header

            try:
                decoded_auth_token = self.token_client.validate_token(auth_token)
            except:
                raise ValueError("Invalid JWT token: validation error")

            return auth_util.get_subject(decoded_auth_token)
        except Exception as e:
            if self.qradar_client is not None:
                decoded_auth_token = jwt.decode(auth_token, verify=False)
                iam_id = decoded_auth_token.get('iam_id', 'NO-NAME')
                self.qradar_client.log_request_auth_failed(request, iam_id)
            raise exceptions.UnauthorizedError(str(e))

    def assert_can_write_projects(self, subject):
        if not self.is_authorized(subject, "grafeas.projects.write"):
            raise exceptions.ForbiddenError(
                "Not allowed to write projects: {}".format(subject))

    def assert_can_read_projects(self, subject):
        if not self.is_authorized(subject, "grafeas.projects.read"):
            raise exceptions.ForbiddenError(
                "Not allowed to read projects: {}".format(subject))

    def assert_can_delete_projects(self, subject):
        if not self.is_authorized(subject, "grafeas.projects.delete"):
            raise exceptions.ForbiddenError(
                "Not allowed to delete projects: {}".format(subject))

    def assert_can_write_notes(self, subject):
        if not self.is_authorized(subject, "grafeas.notes.write"):
            raise exceptions.ForbiddenError(
                "Not allowed to write notes: {}".format(subject))

    def assert_can_read_notes(self, subject):
        if not self.is_authorized(subject, "grafeas.notes.read"):
            raise exceptions.ForbiddenError(
                "Not allowed to read notes: {}".format(subject))

    def assert_can_delete_notes(self, subject):
        if not self.is_authorized(subject, "grafeas.notes.delete"):
            raise exceptions.ForbiddenError(
                "Not allowed to delete notes: {}".format(subject))

    def assert_can_write_occurrences(self, subject):
        if not self.is_authorized(subject, "grafeas.occurrences.write"):
            raise exceptions.ForbiddenError(
                "Not allowed to write occurrences: {}".format(subject))

    def assert_can_read_occurrences(self, subject):
        if not self.is_authorized(subject, "grafeas.occurrences.read"):
            raise exceptions.ForbiddenError(
                "Not allowed to read occurrences: {}".format(subject))

    def assert_can_delete_occurrences(self, subject):
        if not self.is_authorized(subject, "grafeas.occurrences.delete"):
            raise exceptions.ForbiddenError(
                "Not allowed to delete occurrences: {}".format(subject))

    def assert_can_write_occurrences_for_others(self, subject):
        if not self.is_authorized(subject, "grafeas.occurrences.write_for_others"):
            raise exceptions.ForbiddenError(
                "Not allowed to write occurrences for others: {}".format(subject))

    def assert_can_delete_occurrences_for_others(self, subject):
        if not self.is_authorized(subject, "grafeas.occurrences.delete_for_others"):
            raise exceptions.ForbiddenError(
                "Not allowed to delete occurrences for others: {}".format(subject))

    def is_authorized(self, subject, action):
        if not self.enabled:
            logger.info("Subject is authorized: {}".format(subject))
            return True

        if subject.type == 'user':
            subject_field_name = "userId"
        elif subject.type == 'service-id':
            subject_field_name = "serviceId"
        else:
            raise ValueError("Unsupported subject type: {}".format(subject.type))

        params = {
            "subject": {
                "iamId": {
                    subject_field_name: subject.id
                }
            },
            "action": action,
            "resource": {
                "attributes": {
                    "serviceName": "grafeas",
                    "accountId": subject.account_id
                }
            }
        }

        try:
            result = self.pep_client.is_authz2(params, self.access_token)
        except pepclient.PDPError as e:
            logger.exception("IAM API key token expired. Regenerating it ...")
            self.access_token = auth_util.get_identity_token(self.iam_base_url, self.api_key)
            result = self.pep_client.is_authz2(params, self.access_token)

        allowed = result['allowed']
        logger.info("Subject {} authorized: {}".format("is" if allowed else "is not", subject))
        return allowed

    @staticmethod
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

    @staticmethod
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


__auth_client = None
__auth_client_lock = threading.Lock()


def get_auth_client():
    global __auth_client
    with __auth_client_lock:
        if __auth_client is None:
            __auth_client = GrafeasAuthClient()
        return __auth_client


def close_auth_client():
    global __auth_client
    with __auth_client_lock:
        if __auth_client is not None:
            __auth_client.close()



