#!/usr/bin/env python3

import cf_deployment_tracker
import connexion
import logging
import sys
import os


# Emit Bluemix deployment event
cf_deployment_tracker.track()

stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(log_formatter)

logger = logging.getLogger("grafeas")
log_level = os.environ.get('LOG_LEVEL', logging.INFO)
logger.setLevel(log_level)
logger.addHandler(stream_handler)

if log_level == "DEBUG":
    try:
       from http.client import HTTPConnection
    except ImportError:
       from httplib import HTTPConnection
    HTTPConnection.debuglevel = 1

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'IBM Grafeas API'})
    grafeas_configure_ssl = os.environ.get('GRAFEAS_CONFIGURE_SSL', "false")
    if grafeas_configure_ssl.lower() == 'true':
        cert_path = os.environ.get('SSL_CERT_PATH')
        cert_key = os.environ.get('SSL_KEY_PATH')

        if cert_path is None:
            logger.error("GRAFEAS_CONFIGURE_SSL is set to true but SSL_CERT_PATH is not set. ")
            sys.exit(1)
        if cert_key is None:
            logger.error("GRAFEAS_CONFIGURE_SSL is set to true but SSL_KEY_PATH is not set.")
            sys.exit(1)

        context = (cert_path, cert_key)
        app.run(port=8080, threaded=True, ssl_context=context)
    else:
        app.run(port=8080, threaded=True)

