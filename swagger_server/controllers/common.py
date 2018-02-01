import os
import threading
from swagger_server.store import Store


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

    store.create_query_index("DT_N", ['doc_type', 'name'])
    store.create_query_index("DT_P", ['doc_type', 'parent'])
    store.create_query_index("DT_NN", ['doc_type', 'noteName'])
    return store
