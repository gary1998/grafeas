#!/usr/bin/env python3

import cf_deployment_tracker
import connexion
import logging
import sys


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
    app.run(port=8080, threaded=True)