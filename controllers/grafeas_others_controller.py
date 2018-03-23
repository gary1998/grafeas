import logging
from util import exceptions

logger = logging.getLogger("grafeas.occurrences")


def get_home_page():
    try:
        with open('static/index.html', 'r') as f:
            data = f.read()
            return data
    except Exception as e:
        logger.exception("An unexpected error was encountered while reading the home page file")
        return exceptions.InternalServerError(str(e)).to_error()
