import logging


logger = logging.getLogger("grafeas.common")


def build_project_doc_id(account_id, project_id):
    return "{}/projects/{}".format(account_id, project_id)


def build_note_doc_id(account_id, project_id, note_id):
    return "{}/projects/{}/notes/{}".format(account_id, project_id, note_id)


def build_occurrence_doc_id(account_id, project_id, occurrence_id):
    return "{}/projects/{}/occurrences/{}".format(account_id, project_id, occurrence_id)


def build_project_name(project_id):
    return "projects/{}".format(project_id)


def build_note_name(project_id, note_id):
    return "projects/{}/notes/{}".format(project_id, note_id)


def build_occurrence_name(project_id, occurrence_id):
    return "projects/{}/occurrences/{}".format(project_id, occurrence_id)


def build_result(status_code, data):
    return data, status_code
