from controllers.auth import AuthClient
import logging
from util import exceptions

from iam_manager.iam.cloud_IAM import CloudIAM
from iam_manager.iam.iam_utils import IamUtils

logger = logging.getLogger("grafeas.sa_auth")


class SecurityAdvisorAuthClient(AuthClient):
    def __init__(self):
        logger.info("Initializing auth client ...")
        iam_utils = IamUtils(logger)
        iam_config = iam_utils.build_iam_configuration_object()
        self.cloud_iam = CloudIAM(iam_config, logger)
        logger.info("Auth client initialized.")

    def close(self):
        pass

    def enable(self, value):
        pass

    def assert_can_write_projects(self, request, account_id):
        pass

    def assert_can_read_projects(self, request, account_id):
        pass

    def assert_can_delete_projects(self, request, account_id):
        pass

    def assert_can_write_notes(self, request, account_id):
        if request.method == 'POST':
            if not self._is_authorized(request, account_id, "security-advisor.metadata.write"):
                raise exceptions.ForbiddenError(
                    "Not allowed to write notes: {}".format(account_id))
        elif request.method == 'PUT':
            if not self._is_authorized(request, account_id, "security-advisor.metadata.update"):
                raise exceptions.ForbiddenError(
                    "Not allowed to update notes: {}".format(account_id))

    def assert_can_read_notes(self, request, account_id):
        if not self._is_authorized(request, account_id, "security-advisor.metadata.read"):
            raise exceptions.ForbiddenError(
                "Not allowed to read notes: {}".format(account_id))

    def assert_can_delete_notes(self, request, account_id):
        if not self._is_authorized(request, account_id, "security-advisor.metadata.delete"):
            raise exceptions.ForbiddenError(
                "Not allowed to delete notes: {}".format(account_id))

    def assert_can_write_occurrences(self, request, account_id):
        if request.method == 'POST':
            if not self._is_authorized(request, account_id, "security-advisor.findings.write"):
                raise exceptions.ForbiddenError(
                    "Not allowed to write occurrences: {}".format(account_id))
        elif request.method == 'PUT':
            if not self._is_authorized(request, account_id, "security-advisor.findings.update"):
                raise exceptions.ForbiddenError(
                    "Not allowed to update occurrences: {}".format(account_id))

    def assert_can_read_occurrences(self, request, account_id):
        if not self._is_authorized(request, account_id, "security-advisor.findings.read"):
            raise exceptions.ForbiddenError(
                "Not allowed to read occurrences: {}".format(account_id))

    def assert_can_delete_occurrences(self, request, account_id):
        if not self._is_authorized(request, account_id, "security-advisor.findings.delete"):
            raise exceptions.ForbiddenError(
                "Not allowed to delete occurrences: {}".format(account_id))

    def _is_authorized(self, request, account_id, action):
        try:
            user_token = request.headers['X-UserToken']
            internal_token = request.headers['Authorization']

            res_service = self.cloud_iam.authorize_internal_service(internal_token)
            if res_service:
                logger.info("Internal service token validation successful")
            else:
                logger.error("Internal service token validation failed")
                return False

            res_user = self.cloud_iam.authorize(user_token, action, account_id)

            if 'allowed' in res_user:
                if not res_user['allowed']:
                    return False
            else:
                return False
        except Exception as e:
            logger.error("Token Validation failed : %s" % str(e))
            return False

        logger.info("Subject {} authorized: {}".format("is" if res_user['allowed'] else "is not", account_id))
        return True
