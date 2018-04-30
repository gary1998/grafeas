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
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'IBM Grafeas API'})
    grafeas_configure_ssl = os.environ.get('GRFAEAS_CONFIGURE_SSL', "false")
    if grafeas_configure_ssl.lower() == 'true':
        cert_path = os.environ.get('SSL_CERT_PATH')
        cert_key = os.environ.get('SSL_CERT_KEY')

        if cert_path is None:
            logger.error("GRFAEAS_CONFIGURE_SSL is set to true but SSL_CERT_PATH is not set. ")
            sys.exit(1)
        if cert_key is None:
            logger.error("GRFAEAS_CONFIGURE_SSL is set to true but SSL_CERT_KEY is not set.")
            sys.exit(1)

        context = (cert_path, cert_key)
        app.run(port=8080, threaded=True, ssl_context=context)
    else:
        app.run(port=8080, threaded=True)