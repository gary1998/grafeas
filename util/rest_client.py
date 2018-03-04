'''
Created on Mar 4, 2016

@author: alberto
'''

import base64
import json
import logging
import requests
import time
from util.math_util import get_ordinal


logger = logging.getLogger("legato.util.rest_client")


class RestClient(object):
    DEFAULT_REQUEST_TIMEOUT = 60
    DEFAULT_MAX_RETRY_COUNT = 5
    DEFAULT_RETRY_INTERVAL  = 1
    
    def __init__(self):
        self.session = requests.Session()

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.close()
        except:
            logger.exception("Unexpected exception while closing session. Ignored")

    def add_basic_auth_header(self, username, password):
        creds = None
        
        if username is not None:
            creds = username
        
        if password is not None:
            creds += ':' + password
        
        if creds is not None:
            base64_creds = base64.encodebytes(creds)[:-1] # trailing \n removed
            self.add_header('Authorization', "Basic {}".format(base64_creds))        

    def add_token_auth_header(self, token):
        self.add_header('Authorization', "token {}".format(token))

    def add_bearer_auth_header(self, token):
        self.add_header('Authorization', "bearer {}".format(token))

    def add_apikey_auth_header(self, token):
        self.add_header('Authorization', "apikey {}".format(token))

    def add_header(self, key, value):
        self.session.headers[key] = value

    def has_header(self, key):
        return key in self.session.headers

    def set_allow_redirects(self, value):
        self.session.allow_redirects = value

    def set_verify(self, value):
        self.session.verify = value
    
    def set_auth(self, username, password):
        self.session.auth = (username, password)

    def get_auth_username(self):
        return self.session.auth[0]

    def get_auth_password(self):
        return self.session.auth[1]

    def get(self, url, headers=None,
            timeout=DEFAULT_REQUEST_TIMEOUT, **kwargs):
        max_retry_count = kwargs.get('max_retry_count', RestClient.DEFAULT_MAX_RETRY_COUNT)
        retry_interval = kwargs.get('retry_interval', RestClient.DEFAULT_RETRY_INTERVAL)
        retry_count = 0
        while True:       
            try:
                response = self.session.get(
                    url, 
                    headers=headers,
                    timeout=timeout, **kwargs)
                return response
            except requests.RequestException as e:
                if retry_count < max_retry_count:
                    retry_count += 1        
                    logger.warning("Possibly recoverable error: exception='%s'", str(e))
                    logger.warning("Retrying GET request (%s time) ...", get_ordinal(retry_count))
                    time.sleep(retry_interval)
                else:
                    raise e

    def post(self, url, data=None, headers=None,
             timeout=DEFAULT_REQUEST_TIMEOUT, **kwargs):
        max_retry_count = kwargs.get('max_retry_count', RestClient.DEFAULT_MAX_RETRY_COUNT)
        retry_interval = kwargs.get('retry_interval', RestClient.DEFAULT_RETRY_INTERVAL)      
        retry_count = 0
        while True:       
            try:
                response = self.session.post(
                    url, 
                    data=data, 
                    headers=headers,
                    timeout=timeout, **kwargs)
                return response
            except requests.RequestException as e:
                if retry_count < max_retry_count:
                    retry_count += 1        
                    logger.warning("Possibly recoverable error: exception='%s'", str(e))
                    logger.warning("Retrying POST request (%s time) ...", get_ordinal(retry_count))
                    time.sleep(retry_interval)
                else:
                    raise e

    def put(self, url, data=None, headers=None,
            timeout=DEFAULT_REQUEST_TIMEOUT, **kwargs):
        max_retry_count = kwargs.get('max_retry_count', RestClient.DEFAULT_MAX_RETRY_COUNT)
        retry_interval = kwargs.get('retry_interval', RestClient.DEFAULT_RETRY_INTERVAL)        
        retry_count = 0
        while True:       
            try:
                response = self.session.put(
                    url, 
                    data=data, 
                    headers=headers,
                    timeout=timeout, **kwargs)
                return response            
            except requests.RequestException as e:
                if retry_count < max_retry_count:
                    retry_count += 1        
                    logger.warning("Possibly recoverable error: exception='%s'", str(e))
                    logger.warning("Retrying PUT request (%s time) ...", get_ordinal(retry_count))
                    time.sleep(retry_interval)
                else:
                    raise e

    def delete(self, url, headers=None,
               timeout=DEFAULT_REQUEST_TIMEOUT, **kwargs):
        max_retry_count = kwargs.get('max_retry_count', RestClient.DEFAULT_MAX_RETRY_COUNT)
        retry_interval = kwargs.get('retry_interval', RestClient.DEFAULT_RETRY_INTERVAL)       
        retry_count = 0
        while True:       
            try:
                response = self.session.delete(
                    url, 
                    headers=headers,
                    timeout=timeout, **kwargs)        
                return response            
            except requests.RequestException as e:
                if retry_count < max_retry_count:
                    retry_count += 1        
                    logger.warning("Possibly recoverable error: exception='%s'", str(e))
                    logger.warning("Retrying DELETE request (%s time) ...", get_ordinal(retry_count))
                    time.sleep(retry_interval)
                else:
                    raise e

    def get_resource(self, url):
        response = self.get(url)
        content = response.content.decode('utf-8')
        resource = json.loads(content)
        return resource

