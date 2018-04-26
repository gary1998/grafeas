# set environment variable
import os
import logging

if not os.environ.get('ACCEPT_HTTP'):
  logging.warn("ACCEPT_HTTP is not set, setting it to true")
  os.environ['ACCEPT_HTTP'] = "true"

if not os.environ.get('GRAFEAS_DB_NAME'):
  logging.warn("GRAFEAS_DB_NAME is not set, setting it to grafeas")
  os.environ['GRAFEAS_DB_NAME'] = "grafeas"
