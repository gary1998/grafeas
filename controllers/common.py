import os
import threading
from grafeas.store import Store


SHARED_ACCOUNT_ID = "$$$SHARED$$$"


__store = None
__store_lock = threading.Lock()


def get_store():
    """
    Opens a new db connection if there is none yet for the current application context.
    """

    global __store
    with __store_lock:
        if __store is None:
            __store = __create_store()

        return __store


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


def __create_store():
    store = Store(
        os.environ['GRAFEAS_URL'],
        os.environ['GRAFEAS_DB_NAME'],
        os.environ['GRAFEAS_USERNAME'],
        os.environ['GRAFEAS_PASSWORD'])

    store.create_query_index("DT_AI",  ['doc_type', 'account_id'])
    store.create_query_index("DT_PDI", ['doc_type', 'project_doc_id'])
    store.create_query_index("DT_NDI", ['doc_type', 'note_doc_id'])
    return store


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