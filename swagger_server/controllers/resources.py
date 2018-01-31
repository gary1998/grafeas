import os
import threading
from swagger_server.store import Store

__store = None
__store_lock = threading.Lock()


def get_store():
    """
    Opens a new db connection if there is none
    yet for the current application context.
    """

    global __store
    with __store_lock:
        if __store is None:
            __store = Store(
                os.environ['GRAFEAS_URL'],
                os.environ['GRAFEAS_DB_NAME'],
                os.environ['GRAFEAS_USERNAME'],
                os.environ['GRAFEAS_PASSWORD'])

        return __store
