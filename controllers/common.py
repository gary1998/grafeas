import logging
from util import exceptions


logger = logging.getLogger("grafeas.common")


def build_project_doc_id(subject_account_id, project_id):
    return "{}/projects/{}".format(subject_account_id, project_id)


def build_note_doc_id(subject_account_id, project_id, note_id):
    return "{}/projects/{}/notes/{}".format(subject_account_id, project_id, note_id)


def build_occurrence_doc_id(subject_account_id, project_id, occurrence_id):
    return "{}/projects/{}/occurrences/{}".format(subject_account_id, project_id, occurrence_id)


def build_project_name(project_id):
    return "projects/{}".format(project_id)


def build_note_name(project_id, note_id):
    return "projects/{}/notes/{}".format(project_id, note_id)


def parse_note_name(note_name, subject_account_id):
    try:
        note_name_parts = note_name.split('/')
        if note_name_parts[0] == "projects":
            # relative name
            return subject_account_id, note_name_parts[1], note_name_parts[3]
        else:
            # absolute name
            return note_name_parts[0], note_name_parts[2], note_name_parts[4]
    except IndexError:
        raise exceptions.BadRequestError("Invalid note name: {}".format(note_name))


def build_occurrence_name(project_id, occurrence_id):
    return "projects/{}/occurrences/{}".format(project_id, occurrence_id)


def build_result(status_code, data):
    return data, status_code


FIELD_NOT_REQUIRED = "$NOT-REQUIRED"
