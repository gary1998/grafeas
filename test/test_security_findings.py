from . import BaseTestCase
from flask import json


XFORCE_PROJECT = {
    "id": "xforce"
}

ALERT_NOTE_1 = {
    "kind": "FINDING",
    "id": "SuspiciousServerCommunication",
    "shortDescription": "Suspicious Communication with an External Suspected Server",
    "longDescription": "One of the pods in this cluster communicates with a server which is either a suspected bot " +
                       "or known to distribute Malware. This may indicate that your pod is compromised.",
    "createTime": "2018-02-04T13:34:34.071264Z",
    "reportedBy": {
        "id": "xforce",
        "title": "IBM X-Force Threat Intelligence Service",
        "href": " http:// documentation url with nice images inside"
    },
    "finding": {
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

ALERT_OCCURRENCE_1_1 = {
    "kind": "FINDING",
    "id": "11",
    "noteName": "projects/xforce/notes/SuspiciousServerCommunication",
    "createTime": "2018-02-03T12:42:10.082053Z",
    "context": {
        "region": "US-South",
        "account": "Account01",
        "resource": "Pod01",
        "service": "Cluster01"
    },
    "finding": {
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
        "dataTransfered": {
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

ALERT_OCCURRENCE_1_2 = {
    "kind": "FINDING",
    "id": "12",
    "noteName": "projects/xforce/notes/SuspiciousServerCommunication",
    "createTime": "2018-02-04T14:45:23.081063Z",
    "context": {
        "region": "US-South",
        "account": "Account01",
        "resource": "Pod02",
        "service": "Cluster01"
    },
    "finding": {
        "certainty": "HIGH",
        "network": {
            "client": {
                "ip": "172.30.1.4",
                "port": 9080
            },
            "server": {
                "ip": "111.90.127.64",
                "port": 9080
            },
            "direction": "Outbound",
            "protocol": "Ethernet/IPv4/TCP"
        }
    }
}

ALERT_OCCURRENCE_1_3 = {
    "kind": "FINDING",
    "id": "13",
    "noteName": "projects/xforce/notes/SuspiciousServerCommunication",
    "createTime": "2018-02-05T21:44:52.047073Z",
    "context": {
        "region": "US-South",
        "account": "Account01",
        "resource": "Pod03",
        "service": "Cluster02"
    },
    "finding": {
        "certainty": "HIGH",
        "network": {
            "client": {
                "ip": "168.33.1.7",
                "port": 8080
            },
            "server": {
                "ip": "112.91.128.32",
                "port": 8080
            },
            "direction": "Outbound",
            "protocol": "Ethernet/IPv4/TCP"
        }
    }
}

KPI_NOTE_2 = {
    "kind": "KPI",
    "id": "NumClients",
    "shortDescription": "IPs approaching cluster",
    "longDescription": "The number of different IPs which approached this cluster",
    "createTime": "2018-02-04T13:34:34.071264Z",
    "reportedBy": {
        "id": "xforce",
        "title": "IBM X-Force Threat Intelligence Service",
        "href": "http:// documentation url with nice images inside"
    },
    "kpi": {
        "aggregationType": "sum"
    }
}

KPI_OCCURRENCE_2_1 = {
    "kind": "KPI",
    "id": "21",
    "noteName": "projects/xforce/notes/NumClients",
    "createTime": "2018-02-05T12:56:02.061882Z",
    "context": {
        "region": "US-South",
        "account": "account_guid",
        "resource": "name of pod",
        "service": "cluster CRN"
    },
    "kpi": {
        "value": 3432
    }
}

MODIFIED_KPI_OCCURRENCE_2_1 = {
    "kind": "KPI",
    "id": "21",
    "noteName": "projects/xforce/notes/NumClients",
    "createTime": "2018-02-05T12:56:02.061882Z",
    "context": {
        "region": "US-South",
        "account": "account_guid",
        "resource": "name of pod",
        "service": "cluster CRN"
    },
    "kpi": {
        "value": 4321
    }
}

OUTLIER_PROJECT = {
    "id": "outlier"
}

ALERT_NOTE_3 = {
    "kind": "FINDING",
    "id": "EgressDeviation",
    "reportedBy": {
        "id": "outlier",
        "title": "IBM Network Analytics Service",
        "href": " http:// documentation url with nice images inside"
    },
    "shortDescription": "Suspected Data Leakage from a Pod",
    "longDescription": "A pods in this cluster sends data to an external IP in volumes that exceed its normal behavior",
    "createTime": "2018-02-04T13:34:34.071264Z",
    "finding": {
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

ALERT_OCCURRENCE_3_1 = {
    "kind": "FINDING",
    "id": "31",
    "noteName": "projects/outlier/notes/EgressDeviation",
    "createTime": "2018-02-05T20:43:12.071982Z",
    "context": {
        "region": "US-South",
        "account": "account_guid",
        "resource": "name of pod",
        "service": "cluster CRN"
    },
    "finding": {
        "certainty": "HIGH",
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
        "dataTransfered": {
            "clientBytes": 102304
        },
        "deviationHighReference": {
            "dataTransfered": {
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
    def test_01_create_project(self):
        self.post_project(XFORCE_PROJECT)

    def test_02_create_note(self):
        self.post_note(XFORCE_PROJECT['id'], ALERT_NOTE_1)

    def test_03_create_occurrence(self):
        self.post_occurrence(XFORCE_PROJECT['id'], ALERT_OCCURRENCE_1_1)

    def test_04_create_occurrence(self):
        self.post_occurrence(XFORCE_PROJECT['id'], ALERT_OCCURRENCE_1_2)

    def test_05_create_occurrence(self):
        self.post_occurrence(XFORCE_PROJECT['id'], ALERT_OCCURRENCE_1_3)

    def test_06_create_note(self):
        self.post_note(XFORCE_PROJECT['id'], KPI_NOTE_2)

    def test_07_create_occurrence(self):
        self.post_occurrence(XFORCE_PROJECT['id'], KPI_OCCURRENCE_2_1)

    def test_08_update_occurrence(self):
        self.put_occurrence(XFORCE_PROJECT['id'], KPI_OCCURRENCE_2_1['id'], MODIFIED_KPI_OCCURRENCE_2_1)

    def test_09_create_project(self):
        self.post_project(OUTLIER_PROJECT)

    def test_10_create_note(self):
        self.post_note(OUTLIER_PROJECT['id'], ALERT_NOTE_3)

    def test_11_create_occurrence(self):
        self.post_occurrence(OUTLIER_PROJECT['id'], ALERT_OCCURRENCE_3_1)

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

    def put_occurrence(self, project_id, occurrence_id, body):
        response = self.client.open(
            path='/v1alpha1/projects/{}/occurrences/{}'.format(project_id, occurrence_id),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "Account01",
                "Authorization": "Authorization-01"
            })
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))