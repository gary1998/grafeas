import logging
import re
from util import exceptions


logger = logging.getLogger("grafeas.common")


#
#   DOC ID -> FULL NAME
#


def build_project_name(project_id):
    return "projects/{}".format(project_id)


def build_project_full_name(author_account_id, project_id):
    return "{}/projects/{}".format(author_account_id, project_id)


def build_note_name(project_id, note_id):
    return "projects/{}/notes/{}".format(project_id, note_id)


def build_note_full_name(author_account_id, project_id, note_id):
    return "{}/projects/{}/notes/{}".format(author_account_id, project_id, note_id)


def build_occurrence_name(project_id, occurrence_id):
    return "projects/{}/occurrences/{}".format(project_id, occurrence_id)


def build_occurrence_full_name(author_account_id, project_id, occurrence_id):
    return "{}/projects/{}/occurrences/{}".format(author_account_id, project_id, occurrence_id)


def parse_note_name(note_name, author_account_id):
    try:
        note_name_parts = note_name.split('/')
        if note_name_parts[0] == "projects":
            # relative name
            return author_account_id, note_name_parts[1], note_name_parts[3]
        else:
            # absolute name
            return note_name_parts[0], note_name_parts[2], note_name_parts[4]
    except IndexError:
        raise exceptions.BadRequestError("Invalid note name: {}".format(note_name))


def build_result(status_code, data):
    return data, status_code


def set_context_account_id(doc, account_id):
    context = doc.get('context')
    if context is not None:
        context['account_id'] = account_id
    else:
        doc['context'] = {'account_id': account_id}


def validate_id(id_):
    # URL safe characters: Alphanumerics [0-9a-zA-Z], special characters $-_.+!*'(),

    if not id_:
        raise exceptions.BadRequestError("ID is empty")

    safe_characters = r'[^0-9a-zA-Z-_\.&%]'
    if re.search(safe_characters, id_):
        raise exceptions.BadRequestError(
            "ID contains invalid characters, only 0-9, a-z, A-Z, and -_.&% are allowed: {}".format(id_))

