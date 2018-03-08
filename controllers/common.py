from flask import request
import logging
import os
import threading
import pepclient
from util import auth_util
from util import qradar_client
from util import cloudant_client


logger = logging.getLogger("grafeas.common")


def build_project_name(project_id):
    return "projects/{}".format(project_id)


def build_project_doc_id(account_id, project_id):
    return "{}/projects/{}".format(account_id, project_id)


def build_note_name(project_id, note_id):
    return "projects/{}/notes/{}".format(project_id, note_id)


def build_note_doc_id(account_id, project_id, note_id):
    return "{}/projects/{}/notes/{}".format(account_id, project_id, note_id)


def build_occurrence_name(project_id, occurrence_id):
    return "projects/{}/occurrences/{}".format(project_id, occurrence_id)


def build_occurrence_doc_id(account_id, project_id, occurrence_id):
    return "{}/projects/{}/occurrences/{}".format(account_id, project_id, occurrence_id)


def build_result(status, data):
    return data, status.value


def build_error(status, detail):
    error = {
        "detail": detail,
        "status": status.value,
        "title": status.description,
        "type": "about:blank"
    }
    return error, status.value


#
# PEP Client initialization and access
#

class GrafeasAuthClient(pepclient.PEPClient):
    def __init__(self, enabled=True):
        self.iam_base_url = os.environ['IAM_BASE_URL']
        self.api_key = os.environ['IAM_API_KEY']
        self.access_token = auth_util.get_identity_token(self.iam_base_url, self.api_key)
        super().__init__(xacml_url=os.environ['IAM_API_BASE_URL'], auth_token=self.access_token)
        self.enabled = enabled

    def enable(self, value):
        self.enabled = value

    def can_write_project(self, subject):
        return self.is_authorized("grafeas.projects.write", subject)

    def can_read_project(self, subject):
        return self.is_authorized("grafeas.projects.read", subject)

    def can_delete_project(self, subject):
        return self.is_authorized("grafeas.projects.delete", subject)

    def can_write_note(self, subject):
        return self.is_authorized("grafeas.notes.write", subject)

    def can_read_note(self, subject):
        return self.is_authorized("grafeas.notes.read", subject)

    def can_delete_note(self, subject):
        return self.is_authorized("grafeas.notes.delete", subject)

    def can_write_occurrence(self, subject):
        return self.is_authorized("grafeas.occurrences.write", subject)

    def can_read_occurrence(self, subject):
        return self.is_authorized("grafeas.occurrences.read", subject)

    def can_delete_occurrence(self, subject):
        return self.is_authorized("grafeas.occurrences.delete", subject)

    def can_write_occurrences_for_others(self, subject):
        # TODO Add action to grafeas service
        return True

    def is_authorized(self, action, subject):
        if not self.enabled:
            logger.info("Subject is authorized: {}".format(subject))
            return True

        if subject.subject_type == 'user':
            subject_field_name = "userId"
        elif subject.subject_type == 'service-id':
            subject_field_name = "serviceId"
        else:
            raise ValueError("Unsupported subject type: {}".format(subject.subject_type))

        params = {
            "subject": {
                "iamId": {
                    subject_field_name: subject.subject_id
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
            logger.info("IAM API key token expired. Regenerating it ...")
            self.access_token = auth_util.get_identity_token(self.iam_base_url, self.api_key)
            result = self.is_authz2(params, self.access_token)

        allowed = result['allowed']
        logger.info("Subject {} authorized: {}".format("is" if allowed else "is not", subject))
        return allowed


__auth_client = None
__auth_client_lock = threading.Lock()


def get_auth_client():
    """
    Opens a new PEP client if there is none yet for the current application context.
    """

    global __auth_client
    with __auth_client_lock:
        if __auth_client is None:
            __auth_client = __init_auth_client()
        return __auth_client


def __init_auth_client():
    logger.info("Initializing Auth client ...")
    auth_client = GrafeasAuthClient()
    logger.info("PEP client initialized.")
    return auth_client


#
# DB initialization and access
#

__db = None
__db_lock = threading.Lock()


def get_db():
    """
    Opens a new db connection if there is none yet for the current application context.
    """

    global __db
    with __db_lock:
        if __db is None:
            __db = __init_db()
        return __db


def __init_db():
    logger.info("Initializing DB client ...")
    db = cloudant_client.CloudantDatabase(
        os.environ['GRAFEAS_URL'],
        os.environ['GRAFEAS_DB_NAME'],
        os.environ['GRAFEAS_USERNAME'],
        os.environ['GRAFEAS_PASSWORD'])

    # Occurrences are partitioned by:
    #   account_id
    # and filtered by:
    #   projectId (optional, defaul = all projects)
    #   kind (optional, default = all kinds)

    db.create_query_index(
        "DT_OAI_TS",
        ['doc_type', 'account_id', 'update_timestamp'])

    # Occurrences are partitioned by:
    #   resource.account_id
    # filtered by:
    #   projectId (optional, defaul = all projects)
    #   kind (optional, default = all kinds)
    #   note_name (optional, default = all note names )
    # and sorted by:
    #   update_timestamp (default)
    #   finding.severity (optional)

    db.create_query_index(
        "DT_PDI_TS",
        ['doc_type', 'project_doc_id', 'update_timestamp'])
    db.create_query_index(
        "DT_NDI_TS",
        ['doc_type', 'note_doc_id', 'update_timestamp'])
    db.create_query_index(
        "DT_CAI_TS_PDI",
        ['doc_type', 'context.account_id', 'update_timestamp', 'project_doc_id'])
    db.create_query_index(
        "DT_CAI_K_NDI_TS",
        ['doc_type', 'context.account_id', 'kind', 'note_doc_id', 'update_timestamp'])
    db.create_query_index(
        "DT_CAI_TS_NDI",
        ['doc_type', 'context.account_id', 'update_timestamp', 'note_doc_id'])
    db.create_query_index(
        "DT_CAI_SEV_TS_NDI",
        ['doc_type', 'context.account_id', 'finding.severity', 'update_timestamp', 'note_doc_id'])

    # 2018-04-15T16:30:00
    db.add_view(
        'time_series',
        'finding_count_by_date_time',
        """
        function(doc) {{
            if (doc.doc_type == "Occurrence" && doc.kind == 'FINDING') {{
                emit([doc.context.account_id, doc.note_doc_id, 
                    parseInt(doc.update_time.substring(0, 4), 10),
                    parseInt(doc.update_time.substring(5, 7), 10), 
                    parseInt(doc.update_time.substring(8, 10), 10),
                    parseInt(doc.update_time.substring(11, 13), 10),
                    parseInt(doc.update_time.substring(14, 16), 10),
                    parseInt(doc.update_time.substring(17, 19), 10)],
                    1);
            }}
        }}
        """,
        '_sum')

    # 2018-W04-2
    db.add_view(
        'time_series',
        'finding_count_by_week_date',
        """
        function(doc) {{
            if (doc.doc_type == "Occurrence" && doc.kind == 'FINDING') {{
                emit([doc.context.account_id, doc.note_doc_id, 
                    parseInt(doc.update_week_date.substring(0, 4), 10),
                    parseInt(doc.update_week_date.substring(6, 8), 10),
                    parseInt(doc.update_week_date.substring(9, 10), 10)],
                    1);
            }}
        }}
        """,
        '_sum')

    logger.info("DB client initialized.")
    return db


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

    config_dir = os.environ['CONFIG']
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
    if qradar_client is not None:
        method, url, source_addr, source_port, dest_addr, dest_port = _get_request_info()
        qradar_client.log_web_service_auth_succeeded(
            method, url, user_name,
            source_addr, source_port,
            dest_addr, dest_port)


def _log_web_service_auth_failed(user_name):
    qradar_client = get_qradar_client()
    if qradar_client is not None:
        method, url, source_addr, source_port, dest_addr, dest_port = _get_request_info()
        qradar_client.log_web_service_auth_failed(
            method, url, user_name,
            source_addr, source_port,
            dest_addr, dest_port)


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

    return (source_addr, source_port)
