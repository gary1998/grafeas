import json
import logging
import uuid
from requests import request
from itertools import product
from copy import deepcopy
from pepclient._metrics import MetricAggregator
import pepclient

from pepclient._default_cache import DefaultCache
from pepclient._token_validation import TokenClient

PDPURL = 'https://iam-api.ng.bluemix.net'
DEFAULT_TTL = 900


class PEPClient(object):
    def __init__(self, pdp_url=None, xacml_url=None, jwks_url=None,
                 request_func=None, cache=None,
                 logger=None, auth_token=None):
        self.pdp_url = pdp_url or PDPURL
        self.xacml_url = xacml_url or PDPURL
        self.jwks_url = jwks_url or PDPURL
        self.request_func = request_func or request
        self.cache = cache or DefaultCache()
        self.logger = logger or logging.getLogger(__name__)
        self.token = auth_token
        self.version = pepclient.__version__ or '1.0'

        # start up a metric aggregation thread
        self.ma = MetricAggregator(pdp_url=PDPURL, period=30,
                                   logger=self.logger,
                                   auth_token=auth_token)
        self.ma.start()

    def finish(self):
        """
        This is the last function that must be called to shut down the metric
        thread gracefully. It will flush all the cache hits and misses to the
        PDP before stopping
        """
        # tell the metric_agg thread to flush any metrics to PDP and quite
        if self.ma is not None:
            self.ma.stopAndFlush()

    def is_authz(self, params, access_token, transaction_id=None,
                 service_name=None):
        """
        Determine if a subject is allowed to perform an action on a resource.
        (returns the answer from the cache if available)
        """
        if not transaction_id:
            transaction_id = uuid.uuid4().hex
        if not service_name:
            service_name = 'Unknown service '

        self.logger.debug('Authz called with ' + json.dumps(params))

        # Check cache.
        allowed = self.cache.get(json.dumps(params))
        if allowed is not None:
            self.ma.collect('hit')
            self.logger.debug('cache hit, allowed={}'.format(allowed))
            return {'allowed': allowed}

        # Query pdp.
        self.ma.collect('miss')
        self.logger.debug('cache miss, need query PDP for policy decision')
        r = self.request_func('POST', self.pdp_url + '/v1/authz', json=params,
                              headers={'Authorization': access_token,
                                       'Transaction-ID': transaction_id,
                                       'X-Forwarded-By':
                                           service_name +
                                           'PEP_Python_client ' +
                                           self.version})
        try:
            body = json.dumps(r.json(), indent=4, sort_keys=True)
        except:
            body = r.text

        if 'Transaction-ID' in r.headers:
            transaction_id = r.headers['Transaction-ID']

        if r.status_code != 200:
            raise_for_error_response(body, transaction_id)

        try:
            result = r.json()
        except:
            raise PDPError("Object from PDP not in Json format: " + r.text,
                           transaction_id)

        # Cache the results.
        params2 = deepcopy(params)
        if 'obligations' in result:
            cache_obs = (x for x in result['obligations']
                         if x['obligationId'] == 'advanced-cache')
            for ob in cache_obs:
                for crn, action in product(ob['crns'], ob['actions']):
                    params2['resource']['crn'] = crn
                    params2['action'] = action
                    self.cache.set(
                        json.dumps(params2),
                        ob['decision'] == 'Permit',
                        ob['max-age'],
                    )

        try:
            decision = result['decision']
        except:
            raise PDPError('Could not find key "decision" in PDP response: ' +
                           r.text, transaction_id)

        # Return result.
        self.logger.debug('PDP returned ' + result['decision'])
        if decision == 'Permit':
            allowed = True
        elif decision == 'Deny':
            allowed = False
        else:
            PDPError("Unknown decision from PDP: " + decision, transaction_id)
        return {
            'allowed': allowed,
            'transaction_id': transaction_id,
        }

    def is_authz2(self, params, access_token, transaction_id=None,
                  service_name=None):
        """
        Determine if a subject is allowed to perform an action on a resource.
        (returns the answer from the cache if available)
        """
        if not transaction_id:
            transaction_id = uuid.uuid4().hex
        if not service_name:
            service_name = 'Unknown service '

        self.logger.debug('Authz called with ' + json.dumps(params))

        # Check cache.
        allowed = self.cache.get(json.dumps(params))
        if allowed is not None:
            self.ma.collect('hit')
            self.logger.debug('cache hit, allowed={}'.format(allowed))
            return {'allowed': allowed}

        # Query PDP.
        self.ma.collect('miss')
        self.logger.debug('cache miss, need query PDP for policy decision')
        r = self.request_func('POST',
                              self.xacml_url + '/v2/authz',
                              json=[params],
                              headers={'Authorization': access_token,
                                       'Accept':
                                           'application/vnd.authz.v2+json',
                                       'Transaction-ID': transaction_id,
                                       'X-Forwarded-By':
                                           service_name +
                                           'PEP_Python_client ' +
                                           self.version})
        try:
            body = json.dumps(r.json(), indent=4, sort_keys=True)
        except:
            body = r.text

        if 'Transaction-ID' in r.headers:
            transaction_id = r.headers['Transaction-ID']

        if r.status_code != 200:
            raise_for_error_response(body, transaction_id)

        try:
            result = r.json()
        except:
            raise PDPError("Object from XACML not in Json format: " + r.text,
                           transaction_id)

        allowed = False
        # Cache the results.
        params2 = deepcopy(params)

        if 'responses' in result:
            response_obs = (x for x in result['responses'])
            for ob in response_obs:
                try:
                    authorizationDecision = ob['authorizationDecision']
                    allowed = authorizationDecision['permitted']
                except:
                    raise PDPError('Could not find authorizationDecision ' +
                                   ' in XACML response: ' + r.text,
                                   transaction_id)

                if 'obligation' in authorizationDecision:
                    cache_obs = authorizationDecision['obligation']
                    if 'resources' in cache_obs and 'actions' in cache_obs:
                        for crn, action in product(cache_obs['resources'],
                                                   cache_obs['actions']):
                            params2['resource']['crn'] = crn
                            params2['action'] = action
                            self.cache.set(
                               json.dumps(params2),
                               allowed,
                               cache_obs['maxCacheAgeSeconds'],
                            )

        # Return result.
        self.logger.debug('XACML returned ' + str(allowed))
        return {
            'allowed': allowed,
            'transaction_id': transaction_id,
        }

    def getSubjectFromToken(self, jwkToken):
        """
        Processes a jwk token (string) and returns a "Subject" object
        which contains a iamId or attributes object.
        (returns the subject)
        """
        tkClient = TokenClient(
            iam_endpoint=self.jwks_url
        )

        return tkClient.getSubjectAsIamIdClaim(jwkToken)


class PDPError(Exception):
    def __init__(self, message, transaction_id, error_code='Unknown'):
        super(PDPError, self).__init__(message, transaction_id, error_code)
        self.transaction_id = transaction_id
        self.error_code = error_code


def raise_for_error_response(body, transaction_id):
    error = {'transaction_id': transaction_id}

    try:
        error['message'] = str(json.loads(body)['error']['message'])
    except:
        error['message'] = body

    try:
        error['error_code'] = str(json.loads(body)['error']['code'])
    except:
        error['error_code'] = 'Unknown'

    raise PDPError('Error calling PDP: ' +
                   json.dumps(error, indent=4, sort_keys=True),
                   transaction_id, error_code=error['error_code'])