# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import json
from util import dict_util
from .common_ut import BaseTestCase


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

        result = dict_util.override(n, o)
        self.assertDictEqual(result, expected_result,
                             "Result is not what was expected: {}".format(json.dumps(result)))

    def test_02(self):
        n = {
            "severity": "MEDIUM",
            "next_steps": [
                {
                    "title": "step-1"
                },
                {
                    "title": "step-2"
                }
            ]
        }

        o = {
            "certainty": "HIGH",
            "next_steps": [
                {
                    "url": "https:///www.ibm.com"
                }
            ]
        }

        expected_result = {
            "severity": "MEDIUM",
            "certainty": "HIGH",
            "next_steps": [
                {
                    "title": "step-1",
                    "url": "https:///www.ibm.com"
                }
            ]
        }

        result = dict_util.override(n, o)
        self.assertDictEqual(result, expected_result,
                             "Result is not what was expected: {}".format(json.dumps(result)))

    def test_03(self):
        n = {
            "severity": "MEDIUM",
            "next_steps": [
                {
                    "title": "step-1"
                },
                {
                    "title": "step-2"
                },
                {
                    "title": "step-3"
                }
            ]
        }

        o = {
            "certainty": "HIGH",
            "next_steps": [
                {
                },
                {
                },
                {
                    "url": "https:///www.ibm.com"
                }
            ]
        }

        expected_result = {
            "severity": "MEDIUM",
            "certainty": "HIGH",
            "next_steps": [
                {
                    "title": "step-1"
                },
                {
                    "title": "step-2"
                },
                {
                    "title": "step-3",
                    "url": "https:///www.ibm.com"
                }
            ]
        }

        result = dict_util.override(n, o)
        self.assertDictEqual(result, expected_result,
                             "Result is not what was expected: {}".format(json.dumps(result)))

    def test_04(self):
        n = {
            "severity": "MEDIUM",
            "override": "xyz",
            "next_steps": [
                {
                    "title": "step-1"
                },
                {
                    "title": "step-2"
                },
                {
                    "title": "step-3"
                }
            ]
        }

        o = {
            "certainty": "HIGH",
            "override": "123",
            "next_steps": [
                {
                },
                {
                },
                {
                    "url": "https:///www.ibm.com"
                }
            ]
        }

        expected_result = {
            "severity": "MEDIUM",
            "certainty": "HIGH",
            "override": "123",
            "next_steps": [
                {
                    "title": "step-1"
                },
                {
                    "title": "step-2"
                },
                {
                    "title": "step-3",
                    "url": "https:///www.ibm.com"
                }
            ]
        }

        result = dict_util.override(n, o)
        self.assertDictEqual(result, expected_result,
                             "Result is not what was expected: {}".format(json.dumps(result)))
