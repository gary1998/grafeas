from controllers.auth import AuthClient
import logging
import jwt
import os
import json
from util import exceptions
from util import auth_util

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
            return self._validate_token_and_action(
                request, "security-advisor.metadata.write", account_id,
                "Not allowed to write notes")
        elif request.method == 'PUT':
            return self._validate_token_and_action(
                request, "security-advisor.metadata.update", account_id,
                "Not allowed to update notes")

    def assert_can_read_notes(self, request, account_id):
        return self._validate_token_and_action(
            request, "security-advisor.metadata.read", account_id,
            "Not allowed to read notes")

    def assert_can_delete_notes(self, request, account_id):
        return self._validate_token_and_action(
            request, "security-advisor.metadata.delete", account_id,
            "Not allowed to delete notes")

    def assert_can_write_occurrences(self, request, account_id):
        if request.method == 'POST':
            return self._validate_token_and_action(
                request, "security-advisor.findings.write", account_id,
                "Not allowed to write occurrences")
        elif request.method == 'PUT':
            return self._validate_token_and_action(
                request, "security-advisor.findings.update", account_id,
                "Not allowed to update occurrences")

    def assert_can_read_occurrences(self, request, account_id):
        return self._validate_token_and_action(
            request, "security-advisor.findings.read", account_id,
            "Not allowed to read occurrences")

    def assert_can_delete_occurrences(self, request, account_id):
        return self._validate_token_and_action(
            request, "security-advisor.findings.delete", account_id,
            "Not allowed to delete occurrences")

    def _validate_token_and_action(self, request, action, account_id, message):
        subject = self._get_subject(request)
        whitelisted_entity = os.environ.get('WHITELISTED_ENTITY')
        if whitelisted_entity:
            whitelisted_entity = json.loads(whitelisted_entity)
            for whitelist in whitelisted_entity:
                if subject.account_id == whitelist['account']:
                    if subject.id == whitelist['id']:
                        return subject
        if not self._is_authorized(request, action, account_id):
            raise exceptions.ForbiddenError("{}: {}".format(message, subject))
        return subject

    def _get_subject(self, request):
        try:
            auth_header = request.headers['X-UserToken']
            decoded_auth_token = jwt.decode(auth_header[7:], verify=False)
        except:
            raise ValueError("Invalid JWT token: decode error")

        return auth_util.get_subject(decoded_auth_token)

    def _is_authorized(self, request, action, account_id):
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
