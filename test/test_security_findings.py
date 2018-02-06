ALERT_NOTE_1 = {
    "kind": "SECURITY_FINDING",
    "name": "xforce/SuspiciousServerCommunication",
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
        "severity": "High",
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
    "name": "xforce/5353323",
    "noteName": "xforce/SuspiciousServerCommunication",
    "createTime": "2018-02-05T21:44:52.081063Z",
    "context": {
        "region": "US-South",
        "account": "account_guid",
        "service": "cluster CRN",
        "name": "name of pod"
    },
    "security_finding": {
        "certainty": 70,
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
    "name": "xforce/NumClients",
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
    "name": "xforce/NumClients/1234",
    "noteName": "xforce/NumClients",
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

ALERT_NOTE_2 = {
    "kind": "SECURITY_FINDING",
    "name": "outlier/EgressDeviation",
    "reportedBy": {
        "id": "outlier",
        "title": "IBM Network Analytics Service",
        "href": " http:// documentation url with nice images inside"
    },
    "shortDescription": "Suspected Data Leakage from a Pod",
    "longDescription": "A pods in this cluster sends data to an external IP in vlumes that exceed its normal behaviour",
    "security_finding_type": {
        "severity": "Med",
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
    "name": "outlier/EgressDeviation/1982376232",
    "noteName": "outlier/EgressDeviation",
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
