# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import time
from threading import Thread, RLock
from requests import request
import json

HIT_NAME = "cache.hit.count"
MISS_NAME = "cache.miss.count"


class MetricAggregator(Thread):
    """
    This class handles collecting the cache hits and misses for 30
    second increments It then sends them to the PDP which forwards
    them to the metrics collection system. Note that it was not
    implemented as a daemon thread because of the lost of data
    when the main thread is terminated.
    """

    def __init__(self, pdp_url=None, period=30, logger=None, auth_token=None):
        Thread.__init__(self)
        self.nHits = 0
        self.nMisses = 0
        self.pdpUrl = pdp_url
        self.logger = logger
        self.collect_lock = RLock()
        self.allDone = (self.pdpUrl is None or auth_token is None)
        self.token = auth_token
        self.period = period
        self.logger = logger

    def stopAndFlush(self):
        # flush any metrics to PDP and quite
        self.allDone = True

    def run(self):
        if self.pdpUrl is not None and self.token is not None:
            while self.allDone is not True:
                time.sleep(self.period)
                # send our metrics to PDP
                with self.collect_lock:
                    if self.nMisses > 0 or self.nHits > 0:
                        params = {"pep_metrics": [
                            [HIT_NAME, self.nHits],
                            [MISS_NAME, self.nMisses]
                        ]}
                    else:
                        params = None
                    # clear out the collection variables
                    self.nMisses = 0
                    self.nHits = 0
                if params is not None:
                    self.forward_to_pdp(params)

            # send final set of metrics to PDP
            with self.collect_lock:
                # only send if we have counts > 0
                if self.nMisses > 0 or self.nHits > 0:
                    params = {"pep_metrics": [
                       [HIT_NAME, self.nHits],
                       [MISS_NAME, self.nMisses]
                    ]}
                    self.forward_to_pdp(params)
        else:
            if self.logger is not None:
                self.logger.info('Metrics not being collected, '
                                 'need a valid pdp url and '
                                 'authorization token')
            else:
                print('Metrics not being collected, '
                      'need a valid pdp url and '
                      'authorization token')

    def collect(self, cache_action):
        with self.collect_lock:
            if cache_action is 'hit':
                self.nHits += 1
            if cache_action is 'miss':
                self.nMisses += 1

    def forward_to_pdp(self, params):
        if self.token is None:
            self.logger.error('No access token defined')
        else:
            r = request('POST', self.pdpUrl + '/v1/pep_metrics', json=params,
                        headers={'X-Auth': self.token})
            if r.status_code != 201:
                self.logger.error('PDP metrics to \"{}\" call failed, '
                                  'status_code {:d}'.format(self.pdpUrl,
                                                            r.status_code))
            else:
                self.logger.debug('PDP metrics sent, {}'.format(
                    json.dumps(params)))