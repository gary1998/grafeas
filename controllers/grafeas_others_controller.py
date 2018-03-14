import logging


logger = logging.getLogger("grafeas.occurrences")


def get_home_page():
    try:
        with open('static/index.html', 'r') as f:
            data = f.read()
            return data
    except:
        logger.exception("An unexpected error was encountered while getting the home page")
        raise