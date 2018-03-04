import logging
import os
import threading
import pepclient
from util import auth_util
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
        super().__init__(pdp_url=os.environ['PDP_BASE_URL'])
        self.api_base_url = os.environ['IAM_API_BASE_URL']
        self.api_key = os.environ['IAM_API_KEY']
        self.access_token = auth_util.get_identity_token(self.api_base_url, self.api_key)
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

    def is_authorized(self, action, subject):
        if not self.enabled:
            logger.info("Subject is authorized: {}".format(subject))
            return True

        params = {
            "action": action,
            "subject": {
                "id": subject.subject_id,
                "type": subject.subject_type
            },
            "resource": {
                "attributes": {
                    "serviceName": "grafeas"
                }
            }
        }

        try:
            result = self.is_authz(params, self.access_token)
        except pepclient.PEDError as e:
            logger.info("IAM API key token expired. Regenerating it ...")
            self.access_token = auth_util.get_identity_token(self.api_base_url, self.api_key)
            result = self.is_authz(params, self.access_token)

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

    db.create_query_index(
        "DT_OAI_TS",
        ['doc_type', 'account_id', 'update_timestamp'])
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
