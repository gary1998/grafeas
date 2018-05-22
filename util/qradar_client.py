'''
Created on Oct 11, 2017

@author: alberto
'''

import datetime
import json
import logging
from util.syslog_client import SysLogClient


logger = logging.getLogger("util.qradar_client")


# Example: 
# <182>1 2017-01-18T20:16:12.163Z ng.bluemix.net otc-tiam - - - {"res":"\/identity\/v1\/whoami","src":"169.46.120.117","url":"https:\/\/tiam.ng.bluemix.net\/identity\/v1\/whoami","oper":"GET","event":"Web Service Login Succeeded","usrName":"pipeline"}


class QRadarClient(SysLogClient):
    #
    #   High level logging
    #
    _EVENT_WEB_SERVICE_LOGIN_SUCCEEDED = "Web Service Login Succeeded"
    _EVENT_WEB_SERVICE_LOGIN_FAILED = "Web Service Login Failed"
    _EVENT_WEB_SERVICE_LOGOUT = "Web Service Logout"
    
    def __init__(self, host, port,
                 app_id, comp_id, 
                 facility=SysLogClient.LOG_USER, 
                 private_key_file=None, cert_file=None, ca_certs_file=None):
        super().__init__(host, port, facility, private_key_file, cert_file, ca_certs_file)
        self.app_id = app_id
        self.comp_id = comp_id

    def close(self):
        super().close()
    
    def log_web_service_auth_succeeded(
            self, method, url, user_name, 
            source_addr=None, source_port=None, 
            dest_addr=None, dest_port=None):
        message = self.encode_message(
            QRadarClient._EVENT_WEB_SERVICE_LOGIN_SUCCEEDED,
            method, url, user_name,
            source_addr, source_port,
            dest_addr, dest_port)
        self.log(SysLogClient.LOG_INFO, message)
            
    def log_web_service_auth_failed(
            self, method, url, user_name, 
            source_addr=None, source_port=None, 
            dest_addr=None, dest_port=None):
        message = self.encode_message(
            QRadarClient._EVENT_WEB_SERVICE_LOGIN_FAILED,
            method, url, user_name,
            source_addr, source_port,
            dest_addr, dest_port)
        self.log(SysLogClient.LOG_ERR, message)

    def encode_message(self, 
            event, method, url, user_name,
            source_addr=None, source_port=None, 
            dest_addr=None, dest_port=None):
        payload = {
            'event': event,
            "oper": method,
            "url": url
        }

        if user_name is not None:
            payload['usrName'] = user_name
        
        if source_addr is not None:
            payload['src'] = source_addr

        if source_port is not None:
            payload['srcPort'] = source_port

        if dest_addr is not None:
            payload['dst'] = dest_addr

        if dest_port is not None:
            payload['dstPort'] = dest_port

        current_datetime = datetime.datetime.utcnow()
        iso_current_time = current_datetime.isoformat() + 'Z'
        message = "1 {} {} {} - - - {}".format(
            iso_current_time,
            self.app_id,
            self.comp_id,
            json.dumps(payload))        
        return message

    def log_request_auth_succeeded(self, request, user_name):
        try:
            method, url, source_addr, source_port, dest_addr, dest_port = QRadarClient._get_request_info(request)
            self.log_web_service_auth_succeeded(
                method, url, user_name,
                source_addr, source_port,
                dest_addr, dest_port)
        except:
            # QRadar is not available, skip this
            logger.exception("Unexpected error while sending 'web service auth succeeded' record to QRadar")

    def log_request_auth_failed(self, request, user_name):
        try:
            method, url, source_addr, source_port, dest_addr, dest_port = QRadarClient._get_request_info(request)
            self.log_web_service_auth_failed(
                method, url, user_name,
                source_addr, source_port,
                dest_addr, dest_port)
        except:
            # QRadar is not available, skip this
            logger.exception("Unexpected error while sending 'web service auth failed' record to QRadar")

    @staticmethod
    def _get_request_info(request):
        env = request.environ
        method = env['REQUEST_METHOD']
        url = request.url
        source_addr, source_port = QRadarClient._get_request_source(request)
        host_n_port = env['HTTP_HOST'].split(':')
        dest_addr = host_n_port[0]
        dest_port = host_n_port[1] if len(host_n_port) == 2 else "80"
        return method, url, source_addr, source_port, dest_addr, dest_port

    @staticmethod
    def _get_request_source(request):
        env = request.environ
        headers = request.headers

        if headers.getlist("X-Forwarded-For"):
            forwarded_for = request.headers.getlist("X-Forwarded-For")[0]
            source_addrs = forwarded_for.split(',')
            source_addr = source_addrs[0].strip()
        else:
            source_addr = env['REMOTE_ADDR']

        if headers.getlist("X-Forwarded-Port"):
            forwarded_port = request.headers.get("X-Forwarded-Port")
            source_port = forwarded_port.strip()
        else:
            source_port = env['REMOTE_PORT']

        return source_addr, source_port

