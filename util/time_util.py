'''
Created on Apr 14, 2017

@author: alberto
'''

import datetime
import isodate
import time


def utc_iso8601_from_timestamp(timestamp: float):
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    return dt.isoformat()


def utc_timestamp_from_iso8601(s: str):
    return isodate.parse_datetime(s)


def utc_timestamp_now():
    now = datetime.datetime.utcnow()
    return now.timestamp()


def timeit(func):
    def timed(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()

        print("ELAPSED TIME: {:>5.2f}s {}.{}".format(te - ts, func.__module__, func.__name__))
        return result

    return timed
