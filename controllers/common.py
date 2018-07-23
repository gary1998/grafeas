import logging
import re
from util import exceptions


logger = logging.getLogger("grafeas.common")


#
#   DOC ID -> FULL NAME
#

def build_provider_name(account_id, provider_id):
    return "{}/providers/{}".format(account_id, provider_id)


def build_note_name(account_id, provider_id, note_id):
    return "{}/providers/{}/notes/{}".format(account_id, provider_id, note_id)


def build_occurrence_name(account_id, provider_id, occurrence_id):
    return "{}/providers/{}/occurrences/{}".format(account_id, provider_id, occurrence_id)


def parse_note_name(note_name):
    try:
        note_name_components = note_name.split('/')
        if len(note_name_components) != 5:
            raise exceptions.BadRequestError("Invalid note name: {}".format(note_name))

        return note_name_components[0], note_name_components[2], note_name_components[4]
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

