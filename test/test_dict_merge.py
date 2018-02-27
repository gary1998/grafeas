import json
from util import dict_util
from . import BaseTestCase


class TestMockData(BaseTestCase):
    def test_01(self):
        n = {
            "severity": "MEDIUM"
        }

        o = {
            "certainty": "HIGH"
        }

        expected_result = {
            "severity": "MEDIUM",
            "certainty": "HIGH"
        }

        result = dict_util.dict_merge(n, o)
        self.assertDictEqual(result, expected_result, "Result is not what was expected: {}".format(json.dumps(result)))

    def test_02(self):
        n = {
            "severity": "MEDIUM",
            "next_steps": [
                {
                    "title": "step1"
                },
                {
                    "title": "step2"
                }
            ]
        }

        o = {
            "certainty": "HIGH",
            "next_steps": [
                {
                    "url": "https:///www.ibm.com"
                },
                {
                }
            ]
        }

        expected_result = {
            "severity": "MEDIUM",
            "certainty": "HIGH",
            "next_steps": [
                {
                    "title": "step1",
                    "url": "https:///www.ibm.com"
                },
                {
                    "title": "step2"
                }
            ]
        }

        result = dict_util.dict_merge(n, o)
        self.assertDictEqual(result, expected_result, "Result is not what was expected: {}".format(json.dumps(result)))
