import http
import logging
import http.client
from util import exceptions

KEYPROTECT_ROOT_KEY = None

logger = logging.getLogger("grafeas.others")


def get_home_page():
    try:
        with open('static/index.html', 'r') as f:
            data = f.read()
            return data
    except Exception as e:
        logger.exception("An unexpected error was encountered while reading the home page file")
        return exceptions.InternalServerError(str(e)).to_error()


def get_readiness():
    return "Readiness check successful", http.HTTPStatus.OK


def get_liveness():
    return {"ok": True}, http.HTTPStatus.OK
