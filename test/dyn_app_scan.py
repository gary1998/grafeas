import json
import os
from test import common_fvt


OK = 200
NOT_FOUND = 404
CONFLICT = 409


class DynAppScan(common_fvt.CommonFVT):
    def __init__(self, api_base_url):
        super().__init__(api_base_url)

    #
    #   Projects
    #

    def test_create_project(self):
        body = {
            "id": "project01"
        }

        response = self.post_project(body)
        self.assert_status(response, OK)

    def test_create_duplicate_project(self):
        body = {
            "id": "Project01"
        }

        response = self.post_project(body)
        self.assert_status(response, CONFLICT)

    def test_get_project(self):
        response = self.get_project("project01")
        self.assert_status(response, OK)

    def test_list_projects(self):
        response = self.get_projects()
        self.assert_status(response, OK)
        results = json.loads(response.content.decode('utf-8'))
        self.assert_true(len(results) > 0, "An array of one or more projects was expected.")


    #
    #   Notes
    #

    def test_create_note(self):
        body = {
            "id": "Note01",
            "short_description": "The short description of Note01",
            "long_description": "The long description of Note01",
            "kind": "FINDING",
            "finding": {
                "severity": "HIGH"
            }
        }

        response = self.post_note('project01', body)
        self.assert_status(response, OK)

    def test_create_duplicate_note(self):
        body = {
            "id": "Note01",
            "short_description": "The short description of Note01",
            "long_description": "The long description of Note01",
            "kind": "FINDING",
            "finding": {
                "severity": "HIGH"
            }
        }

        response = self.post_note('project01', body)
        self.assert_status(response, CONFLICT)

    def test_get_note(self):
        response = self.get_note('project01', 'Note01')
        self.assert_status(response, OK)

    def test_list_notes(self):
        response = self.get_notes('project01')
        self.assert_status(response, OK)
        results = json.loads(response.content.decode('utf-8'))
        self.assert_true(len(results) > 0, "An array of one or more notes was expected.")

    def test_update_note(self):
        body = {
            "id": "Note01",
            "short_description": "The updated short description of Note01",
            "long_description": "The updated long description of Note01",
            "kind": "FINDING",
            "finding": {
                "severity": "HIGH"
            }
        }

        response = self.put_note('project01', 'Note01', body)
        self.assert_status(response, OK)


#
#   Occurrences
#

    def test_create_occurrence(self):
        body = {
            "id": "Occurrence01",
            "note_name": "projects/project01/notes/Note01",
            "short_description": "The short description of Occurrence01",
            "long_description": "The long description of Occurrence01",
            "kind": "FINDING",
            "finding": {
                "certainty": "MEDIUM"
            },
            "context": {
                "account_id": os.environ['RESOURCE_ACCOUNT_ID']
            }
        }

        response = self.post_occurrence('project01', body)
        self.assert_status(response, OK)

    def test_create_duplicate_occurrence(self):
        body = {
            "id": "Occurrence01",
            "note_name": "projects/project01/notes/Note01",
            "short_description": "A different short description of Occurrence01",
            "long_description": "A different long description of Occurrence01",
            "kind": "FINDING",
            "finding": {
                "certainty": "HIGH"
            },
            "context": {
                "account_id": os.environ['RESOURCE_ACCOUNT_ID']
            }
        }

        response = self.post_occurrence('project01', body)
        self.assert_status(response, CONFLICT)

    def test_create_or_update_occurrence(self):
        body = {
            "id": "Occurrence01",
            "note_name": "projects/project01/notes/Note01",
            "short_description": "Updated short description of Occurrence01",
            "long_description": "Updated long description of Occurrence01",
            "kind": "FINDING",
            "finding": {
                "certainty": "HIGH"
            },
            "context": {
                "account_id": os.environ['RESOURCE_ACCOUNT_ID']
            }
        }

        response = self.post_or_put_occurrence('project01', body)
        self.assert_status(response, OK)

    def test_get_occurrence(self):
        response = self.get_occurrence('project01', 'Occurrence01')
        self.assert_status(response, OK)

    def test_get_occurrence_note(self):
        response = self.get_occurrence_note('project01', 'Occurrence01')
        self.assert_status(response, OK)

    def test_list_occurrences(self):
        response = self.get_occurrences('project01')
        self.assert_status(response, OK)
        results = json.loads(response.content.decode('utf-8'))
        self.assert_true(len(results) > 0, "A array of one ore more occurrences was expected.")

    def test_list_note_occurrences(self):
        response = self.get_note_occurrences('project01', 'Note01')
        self.assert_status(response, OK)
        results = json.loads(response.content.decode('utf-8'))
        self.assert_true(len(results) > 0, "An array of one or more occurrences was expected.")


    #
    # Cleanup
    #

    def test_delete_occurrence(self):
        response = self.delete_occurrence('project01', 'Occurrence01')
        self.assert_status(response, OK)

    def test_delete_missing_occurrence(self):
        response = self.delete_occurrence('project01', 'Occurrence01')
        self.assert_status(response, NOT_FOUND)

    def test_delete_note(self):
        response = self.delete_note('project01', 'Note01')
        self.assert_status(response, OK)

    def test_delete_missing_note(self):
        response = self.delete_note('project01', 'Note01')
        self.assert_status(response, NOT_FOUND)

    def test_delete_project(self):
        response = self.delete_project("project01")
        self.assert_status(response, OK)

    def test_delete_missing_project(self):
        response = self.delete_project("project01")
        self.assert_status(response, NOT_FOUND)


if __name__ == '__main__':
    test = DynAppScan(api_base_url="https://grafeas.ng.bluemix.net")
    test.test_create_project()
    test.test_create_duplicate_project()
    test.test_get_project()
    test.test_list_projects()
    test.test_create_note()
    test.test_create_duplicate_note()
    test.test_get_note()
    test.test_list_notes()
    test.test_update_note()
    test.test_create_occurrence()
    test.test_create_duplicate_occurrence()
    test.test_create_or_update_occurrence()
    test.test_get_occurrence()
    test.test_get_occurrence_note()
    test.test_list_occurrences()
    test.test_list_note_occurrences()
    test.test_delete_occurrence()
    test.test_delete_missing_occurrence()
    test.test_delete_note()
    test.test_delete_missing_note()
    test.test_delete_project()
    test.test_delete_missing_project()

