from . import BaseTestCase
from flask import json
from http import HTTPStatus


XFORCE_PROJECT = {
    "id": "security-advisor"
}

ALERT_NOTE_1 = {
    "kind": "FINDING",
    "id": "xforce-SuspiciousServerCommunication",
    "short_description": "Suspicious Communication with an External Suspected Server",
    "long_description": "One of the pods in this cluster communicates with a server which is either a suspected bot " +
                        "or known to distribute Malware. This may indicate that your pod is compromised.",
    "create_time": "2018-02-04T13:34:34.071264Z",
    "reported_by": {
        "id": "xforce",
        "title": "IBM X-Force Threat Intelligence Service",
        "href": "http:// documentation url with nice images inside"
    },
    "finding_type": {
        "severity": "HIGH",
        "titles": {
            "context": {
                "name": {
                    "title": "Suspected Pod"
                }
            }
        },
        "next_steps": [
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
    "id": "xforce-11",
    "note_name": "projects/security-advisor/notes/xforce-SuspiciousServerCommunication",
    "create_time": "2018-02-03T12:42:10.082053Z",
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
        "data_transfered": {
            "client_bytes": 43431,
            "server_bytes": 901,
            "client_packets": 232,
            "server_packets": 23
        },
        "next_steps": [
            {
                "href": " https://exchange.xforce.ibmcloud.com/ip/111.90.147.66"
            }
        ]
    }
}

ALERT_OCCURRENCE_1_2 = {
    "kind": "FINDING",
    "id": "xforce-12",
    "note_name": "projects/security-advisor/notes/xforce-SuspiciousServerCommunication",
    "create_time": "2018-02-04T14:45:23.081063Z",
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
    "id": "xforce-13",
    "note_name": "projects/security-advisor/notes/xforce-SuspiciousServerCommunication",
    "create_time": "2018-02-05T21:44:52.047073Z",
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
    "id": "xforce-NumClients",
    "short_description": "IPs approaching cluster",
    "long_description": "The number of different IPs which approached this cluster",
    "create_time": "2018-02-04T13:34:34.071264Z",
    "reported_by": {
        "id": "xforce",
        "title": "IBM X-Force Threat Intelligence Service",
        "href": "http:// documentation url with nice images inside"
    },
    "kpi_type": {
        "aggregation_type": "SUM"
    }
}

KPI_OCCURRENCE_2_1 = {
    "kind": "KPI",
    "id": "xforce-21",
    "note_name": "projects/security-advisor/notes/xforce-NumClients",
    "create_time": "2018-02-05T12:56:02.061882Z",
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

OUTLIER_PROJECT = {
    "id": "outlier"
}

ALERT_NOTE_3 = {
    "kind": "FINDING",
    "id": "EgressDeviation",
    "reported_by": {
        "id": "outlier",
        "title": "IBM Network Analytics Service",
        "href": " http:// documentation url with nice images inside"
    },
    "short_description": "Suspected Data Leakage from a Pod",
    "long_description": "A pods in this cluster sends data to an external IP in volumes that exceed its normal behavior",
    "create_time": "2018-02-04T13:34:34.071264Z",
    "finding_type": {
        "severity": "MEDIUM",
        "titles": {
            "context": {
                "name": {
                    "title": "Suspected Pod"
                }
            }
        },
        "next_steps": [
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
    "note_name": "projects/outlier/notes/EgressDeviation",
    "create_time": "2018-02-05T20:43:12.071982Z",
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
        "data_transferred": {
            "client_bytes": 102304
        },
        "deviation_high_reference": {
            "data_transferred": {
                "client_bytes": {
                    "norm_high": 25000,
                    "alert_high": 75000,
                    "units": "MB"
                }
            }
        }
    }
}

MODIFIED_ALERT_OCCURRENCE_3_1 = {
    "kind": "FINDING",
    "id": "31",
    "note_name": "projects/outlier/notes/EgressDeviation",
    "create_time": "2018-02-05T20:43:12.071982Z",
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
        "data_transferred": {
            "client_bytes": 213415
        },
        "deviation_high_reference": {
            "data_transferred": {
                "client_bytes": {
                    "norm_high": 26000,
                    "alert_high": 80000,
                    "units": "MB"
                }
            }
        }
    }
}


class TestSecurityFindings(BaseTestCase):
    def test_01_create_project(self):
        response = self.post_project(XFORCE_PROJECT)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_02_create_note(self):
        response = self.post_note(XFORCE_PROJECT['id'], ALERT_NOTE_1)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_03_create_occurrence(self):
        response = self.post_occurrence(XFORCE_PROJECT['id'], ALERT_OCCURRENCE_1_1)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_04_create_occurrence(self):
        response = self.post_occurrence(XFORCE_PROJECT['id'], ALERT_OCCURRENCE_1_2)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_05_create_occurrence(self):
        response = self.post_occurrence(XFORCE_PROJECT['id'], ALERT_OCCURRENCE_1_3)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_06_create_note(self):
        response = self.post_note(XFORCE_PROJECT['id'], KPI_NOTE_2)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_07_create_occurrence(self):
        response = self.post_occurrence(XFORCE_PROJECT['id'], KPI_OCCURRENCE_2_1)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_08_create_project(self):
        response = self.post_project(OUTLIER_PROJECT)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_09_create_note(self):
        response = self.post_note(OUTLIER_PROJECT['id'], ALERT_NOTE_3)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_10_create_occurrence(self):
        response = self.post_occurrence(OUTLIER_PROJECT['id'], ALERT_OCCURRENCE_3_1)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def test_11_create_occurrence(self):
        response = self.put_occurrence(OUTLIER_PROJECT['id'], MODIFIED_ALERT_OCCURRENCE_3_1['id'],
                                       MODIFIED_ALERT_OCCURRENCE_3_1)
        self.assertStatus(response, HTTPStatus.OK, "Response body is : " + response.data.decode('utf-8'))

    def post_project(self, body):
        return self.client.open(
            path='/v1alpha1/projects',
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                #"Account": "AccountY", Projects are shared by all accounts
                "Authorization": "AuthorizationY"
            })

    def post_note(self, project_id, body):
        return self.client.open(
            path='/v1alpha1/projects/{}/notes'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                #"Account": "AccountY", Notes are shared by all accounts
                "Authorization": "AuthorizationY"
            })

    def post_occurrence(self, project_id, body):
        return self.client.open(
            path='/v1alpha1/projects/{}/occurrences'.format(project_id),
            method='POST',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountY",
                "Authorization": "AuthorizationY"
            })

    def put_occurrence(self, project_id, occurrence_id, body):
        return self.client.open(
            path='/v1alpha1/projects/{}/occurrences/{}'.format(project_id, occurrence_id),
            method='PUT',
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Account": "AccountY",
                "Authorization": "AuthorizationY"
            })
