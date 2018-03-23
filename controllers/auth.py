import logging
import os
import pepclient
import threading
from util import auth_util
from util import exceptions


logger = logging.getLogger("grafeas.auth")


#
# PEP Client initialization and access
#

class GrafeasAuthClient(pepclient.PEPClient):
    def __init__(self, enabled=True):
        logger.info("Initializing auth client ...")
        self.iam_base_url = os.environ['IAM_BASE_URL']
        self.api_key = os.environ['IAM_API_KEY']
        self.access_token = auth_util.get_identity_token(self.iam_base_url, self.api_key)
        super().__init__(xacml_url=os.environ['IAM_API_BASE_URL'], auth_token=self.access_token)
        self.enabled = enabled
        logger.info("Auth client initialized.")

    def enable(self, value):
        self.enabled = value

    def get_subject(self, request):
        try:
            return auth_util.get_subject(request)
        except Exception as e:
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
            result = self.is_authz2(params, self.access_token)
        except pepclient.PDPError as e:
            logger.exception("IAM API key token expired. Regenerating it ...")
            self.access_token = auth_util.get_identity_token(self.iam_base_url, self.api_key)
            result = self.is_authz2(params, self.access_token)

        allowed = result['allowed']
        logger.info("Subject {} authorized: {}".format("is" if allowed else "is not", subject))
        return allowed


__auth_client = None
__auth_client_lock = threading.Lock()


def get_auth_client():
    global __auth_client
    with __auth_client_lock:
        if __auth_client is None:
            __auth_client = GrafeasAuthClient()
        return __auth_client
