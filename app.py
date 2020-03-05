# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
#!/usr/bin/env python3

import cf_deployment_tracker
import connexion
import logging
import sys
import os
import json

os.environ["IAM_CONFIG"] = json.dumps({"adminService":{"serviceName":"Grafeas-Admin-Service","serviceid":"ServiceId-1d1e8188-8ae6-45a4-b67e-5058a8373638"},"externalService":{"apiKey":"pYgIUhpGO25tN52EtbuzzomqGX_D7h_La8PCD_ELj6cq","serviceName":"Grafeas-External-Service","serviceid":"ServiceId-838121e1-8053-40e0-85d6-43a7d30f110d"},"internalService":{"apiKey":"ZSbLcYWa3iLul8zI4Vc_7tgYN8qG8GF4qmcaFL79713-","serviceName":"Grafeas-Internal-Service","serviceid":"ServiceId-5f4ca4ac-9a64-4bf0-ae03-4ad9a21afe42"},"serviceCname":"staging","viewerService":{"apiKey":"pYgIUhpGO25tN52EtbuzzomqGX_D7h_La8PCD_ELj6cq","serviceName":"security-advisor","serviceid":"ServiceId-838121e1-8053-40e0-85d6-43a7d30f110d"}})

# Emit Bluemix deployment event
cf_deployment_tracker.track()

stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(log_formatter)

logger = logging.getLogger("grafeas")
log_level = os.environ.get('LOG_LEVEL', logging.DEBUG)
logger.setLevel(log_level)
logger.addHandler(stream_handler)
port = int(os.environ.get("PORT", 8081))


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
        app.run(port=port, threaded=True, ssl_context=context)
    else:
        app.run(port=port, threaded=True)