from . import BaseTestCase
from flask import json


XFORCE_PROJECT = {
    "id": "xforce"
}

ALERT_NOTE_1 = {
    "kind": "SECURITY_FINDING",
    "id": "SuspiciousServerCommunication",
    "shortDescription": "Suspicious Communication with an External Suspected Server",
    "longDescription": "One of the pods in this cluster communicates with a server which is either a suspected bot " +
                       "or known to distribute Malware. This may indicate that your pod is compromised.",
    "createTime": "2018-02-04T13:34:34.071264Z",
    "reportedBy": {
        "id": "xforce",
        "title": "IBM X-Force Threat Intelligece Service",
        "href": " http:// documentation url with nice images inside"
    },
    "security_finding_type": {
        "severity": "HIGH",
        "titles": {
            "context": {
                "name": {
                    "title": "Suspected Pod"
                }
            }
        },
        "nextSteps": [
            {
                "title": "Check information about the external suspected server",
                "href": " https://exchange.xforce.ibmcloud.com/"
            },
            {
                "title": "Check the pod to see what is running and which executable is sending out this communication",
                "href": " http:// text documentation"

            }
        ]
    }
}

ALERT_OCCURRENCE_1 = {
    "kind": "SECURITY_FINDING",
    "id": "5353323",
    "noteName": "projects/xforce/notes/SuspiciousServerCommunication",
    "createTime": "2018-02-05T21:44:52.081063Z",
    "context": {
        "region": "US-South",
        "account": "account_guid",
        "service": "cluster CRN",
        "name": "name of pod"
    },
    "security_finding": {
        "certainty": "MEDIUM",
        "network": {
            "client": {
                "ip": "172.30.1.3",
                "port": 9080
            },
            "server": {
                "ip": "111.90.147.66",
                "port": 9080
            },
            "direction": "Outbound",
            "protocol": "Ethernet/IPv4/TCP"
        },
        "data_transfered": {
            "clientBytes": 43431,
            "serverBytes": 901,
            "clientPackets": 232,
            "serverPackets": 23
        },
        "nextSteps": [
            {
                "href": " https://exchange.xforce.ibmcloud.com/ip/111.90.147.66"
            }
        ]
    }
}

KPI_NOTE_1 = {
    "kind": "SECURITY_KPI",
    "id": "NumClients",
    "shortDescription": "IPs approaching cluster",
    "longDescription": "The number of different IPs which approached this cluster",
    "createTime": "2018-02-04T13:34:34.071264Z",
    "reportedBy": {
        "id": "xforce",
        "title": "IBM X-Force Threat Intelligece Service",
        "href": "http:// documentation url with nice images inside"
    },
    "security_kpi_type": {
        "aggregationType": "sum"
    }
}

KPI_OCCURRENCE_1 = {
    "kind": "SECURITY_KPI",
    "id": "1234",
    "noteName": "projects/xforce/notes/NumClients",
    "createTime": "2018-02-05T12:56:02.061882Z",
    "context": {
        "region": "US-South",
        "account": "account_guid",
        "service": "cluster CRN",
    },
    "security_kpi": {
        "value": 3432
    }
}

OUTLIER_PROJECT = {
    "id": "outlier"
}

ALERT_NOTE_2 = {
    "kind": "SECURITY_FINDING",
    "id": "EgressDeviation",
    "reportedBy": {
        "id": "outlier",
        "title": "IBM Network Analytics Service",
        "href": " http:// documentation url with nice images inside"
    },
    "shortDescription": "Suspected Data Leakage from a Pod",
    "longDescription": "A pods in this cluster sends data to an external IP in vlumes that exceed its normal behaviour",
    "security_finding_type": {
        "severity": "MEDIUM",
        "titles": {
            "context": {
                "name": {
                    "title": "Suspected Pod"
                }
            }
        },
        "nextSteps": [
            {
                "title": "Examine this report details to learn the identity of the client Pod and external IP address",
            },
            {
                "title": "Examine this report details to learn how what is the normal behaviour for this Pod",
            },
            {
                "title": "Examine which process in the Pod is sending out the excessive data",
                "href": " http:// text documentation"
            }
        ]
    }
}

ALERT_OCCURRENCE_2 = {
    "kind": "SECURITY_FINDING",
    "id": "1982376232",
    "noteName": "projects/outlier/notes/EgressDeviation",
    "createTime": "2018-02-05T20:43:12.071982Z",
    "certainty": 70,
    "context": {
        "region": "US-South",
        "account": "account_guid",
        "service": "cluster CRN",
        "name": "name of pod"
    },
    "security_finding": {
        "network": {
            "client": {
                "ip": "172.30.1.3",
                "port": 9080
            },
            "server": {
                "ip": "111.90.147.66",
                "port": 9080
            },
            "direction": "Outbound",
            "protocol": "Ethernet/IPv4/TCP"
        },
        "data_transfered": {
            "clientBytes": 102304
        },
        "deviation_high_reference": {
            "data_transfered": {
                "clientBytes": {
                    "normHigh": 25000,
                    "alertHigh": 75000,
                    "units": "MB"
                }
            }
        }
    }
}


class TestSecurityFindings(BaseTestCase):
    """ GrafeasNotesController integration test stubs """

    def test_01_create_project(self):
        self.post_project(XFORCE_PROJECT)

    def test_02_create_note(self):
        self.post_note(XFORCE_PROJECT['id'], ALERT_NOTE_1)

    def test_03_create_occurrence(self):
        self.post_occurrence(XFORCE_PROJECT['id'], ALERT_OCCURRENCE_1)

    def test_04_create_note(self):
        self.post_note(XFORCE_PROJECT['id'], KPI_NOTE_1)

    def test_05_create_occurrence(self):
        self.post_occurrence(XFORCE_PROJECT['id'], KPI_OCCURRENCE_1)

    def test_06_create_project(self):
        self.post_project(OUTLIER_PROJECT)

    def test_07_create_note(self):
        self.post_note(OUTLIER_PROJECT['id'], ALERT_NOTE_2)

    def test_08_create_occurrence(self):
        self.post_occurrence(OUTLIER_PROJECT['id'], ALERT_OCCURRENCE_2)

    def post_project(self, body):
        response = self.client.open(
            path='/v1alpha1/projects',
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def post_note(self, project_id, body):
        response = self.client.open(
            path='/v1alpha1/projects/{}/notes'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def post_occurrence(self, project_id, body):
        response = self.client.open(
            path='/v1alpha1/projects/{}/occurrences'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
