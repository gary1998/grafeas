import connexion
import datetime
from http import HTTPStatus
import isodate
from . import common
from util import auth_util
from util import dict_util
from util import exceptions


def create_occurrence(project_id, body):
    """
    Creates a new &#x60;Occurrence&#x60;. Use this method to create &#x60;Occurrences&#x60; for a resource.

    :param project_id: Part of &#x60;parent&#x60;. This contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: ApiOccurrence
    """

    db = common.get_db()
    auth_client = common.get_auth_client()
    subject = auth_util.get_subject(connexion.request)
    if not auth_client.can_write_occurrence(subject):
        return common.build_error(HTTPStatus.UNAUTHORIZED, "Not allowed to create occurrences: {}".format(subject))

    replace_if_exists_header_value = connexion.request.headers.get('Replace-If-Exists')
    replace_if_exists = replace_if_exists_header_value is not None and replace_if_exists_header_value.lower() == 'true'
    project_doc_id = common.build_project_doc_id(subject.account_id, project_id)

    if 'id' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Missing required field: 'id'")

    occurrence_id = body['id']
    occurrence_name = common.build_occurrence_name(project_id, occurrence_id)

    if 'note_name' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Missing required field: 'note_name'")

    note_name = body['note_name']

    # get the occurrence's note
    try:
        if note_name.startswith("projects/"):
            # relative name
            note_doc_id = "{}/{}".format(subject.account_id, note_name)
        else:
            # absolute name
            note_doc_id = note_name

        note = db.get_doc(note_doc_id)
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Note not found: {}".format(note_name))

    if not note_name.startswith("projects/") and not note['shared']:
        return common.build_error(HTTPStatus.UNAUTHORIZED, "Occurrence's note is not shared")

    if 'kind' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Missing required field: 'kind'")

    kind = body['kind']

    if kind not in ['FINDING', 'KPI', 'CARD_CONFIGURED']:
        return common.build_error(
            HTTPStatus.BAD_REQUEST, "Invalid 'kind' value, only 'CARD_CONFIGURED', 'FINDING', and 'KPI' are allowed")

    if kind == 'FINDING' and 'finding' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST, "Missing field for 'FINDING' occurrence: 'finding'")
    if kind == 'KPI' and 'kpi' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST, "Missing field for 'KPI' occurrence: 'kpi'")
    if kind == 'CARD_CONFIGURED' and 'card_configured' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST, "Missing field for 'CARD_CONFIGURED' occurrence: 'card_configured'")

    if 'context' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Missing required field: 'context'")

    context = body['context']

    if 'account_id' not in context:
        return common.build_error(
            HTTPStatus.BAD_REQUEST, "Missing required field: 'context.account_id'")

    context_account_id = context['account_id']
    if context_account_id != subject.account_id:
        if not auth_client.can_write_occurrences_for_others(subject):
            return common.build_error(HTTPStatus.UNAUTHORIZED, "Not allowed to create occurrences for others")

    body['doc_type'] = 'Occurrence'
    body['account_id'] = subject.account_id
    body['project_id'] = project_id
    body['id'] = occurrence_id
    body['name'] = occurrence_name
    body['project_doc_id'] = project_doc_id
    body['note_doc_id'] = note_doc_id

    if 'create_time' in body:
        create_datetime = isodate.parse_datetime(body['create_time'])
        create_timestamp = create_datetime.timestamp()
    else:
        create_datetime = datetime.datetime.utcnow()
        create_timestamp = create_datetime.timestamp()
        body['create_time'] = create_datetime.isoformat() + 'Z'
    body['update_time'] = body['create_time']
    body['create_timestamp'] = create_timestamp
    body['update_timestamp'] = create_timestamp
    body['update_week_date'] = _week_date_iso_format(create_datetime.isocalendar())

    # set occurrence default values from the associated note values
    _set_occurrence_defaults(body, note)

    # internalize the security value
    _set_internal_occurrence_severity(body)

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(subject.account_id, project_id, occurrence_id)
        db.create_doc(occurrence_doc_id, body)
        return common.build_result(HTTPStatus.OK, _clean_doc(body))
    except exceptions.AlreadyExistsError:
        if replace_if_exists:
            doc = db.update_doc(occurrence_doc_id, body)
            return common.build_result(HTTPStatus.OK, _clean_doc(doc))
        else:
            return common.build_error(HTTPStatus.CONFLICT, "Occurrence already exists: {}".format(occurrence_doc_id))


def update_occurrence(project_id, occurrence_id, body):
    """
    Updates an existing &#x60;Note&#x60;.

    :param project_id: First part of occurrence &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type occurrence_id: str
    :param body:
    :type body: dict | bytes

    :rtype: ApiNote
    """

    db = common.get_db()
    auth_client = common.get_auth_client()
    subject = auth_util.get_subject(connexion.request)
    if not auth_client.can_write_occurrence(subject):
        return common.build_error(HTTPStatus.UNAUTHORIZED, "Not allowed to update occurrences: {}".format(subject))

    if 'id' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Field 'id' is missing")

    if 'note_name' not in body:
        return common.build_error(HTTPStatus.BAD_REQUEST, "Field 'note_name' is missing")

    if 'update_time' in body:
        update_datetime = isodate.parse_datetime(body['update_time'])
        update_timestamp = update_datetime.timestamp()
    else:
        update_datetime = datetime.datetime.utcnow()
        update_timestamp = update_datetime.timestamp()
        body['update_time'] = update_datetime.isoformat() + 'Z'
    body['update_timestamp'] = update_timestamp
    body['update_week_date'] = _week_date_iso_format(update_datetime.isocalendar())

    _set_internal_occurrence_severity(body)

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(subject.account_id, project_id, occurrence_id)
        doc = db.update_doc(occurrence_doc_id, body)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_doc_id))


def list_occurrences(project_id, filter=None, page_size=None, page_token=None):
    """
    Lists active &#x60;Occurrences&#x60; for a given project matching the filters.

    :param project_id: Part of &#x60;parent&#x60;. This contains the project_id for example: projects/{project_id}
    :type project_id: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of occurrences to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListOccurrencesResponse
    """

    db = common.get_db()
    auth_client = common.get_auth_client()
    subject = auth_util.get_subject(connexion.request)
    if not auth_client.can_read_occurrence(subject):
        return common.build_error(HTTPStatus.UNAUTHORIZED, "Not allowed to list occurrences: {}".format(subject))

    project_doc_id = common.build_project_doc_id(subject.account_id, project_id)

    docs = db.find(
        filter_={
            'doc_type': 'Occurrence',
            'project_doc_id': project_doc_id
        },
        index="DT_PDI_TS")
    return common.build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def list_note_occurrences(project_id, note_id, filter=None, page_size=None, page_token=None):
    """
    Lists &#x60;Occurrences&#x60; referencing the specified &#x60;Note&#x60;.
    Use this method to get all occurrences referencing your &#x60;Note&#x60; across all your customer projects.

    :param project_id: First part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type project_id: str
    :param note_id: Second part of note &#x60;name&#x60;: projects/{project_id}/notes/{note_id}
    :type note_id: str
    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of notes to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListNoteOccurrencesResponse
    """

    db = common.get_db()
    auth_client = common.get_auth_client()
    subject = auth_util.get_subject(connexion.request)
    auth_client.can_read_occurrence(subject)
    if not auth_client.can_write_occurrence(subject):
        return common.build_error(
            HTTPStatus.UNAUTHORIZED, "Not allowed to update note's occurrences: {}".format(subject))

    note_doc_id = common.build_note_doc_id(subject.account_id, project_id, note_id)

    docs = db.find(
        filter_={
            'doc_type': 'Occurrence',
            'note_doc_id': note_doc_id
        },
        index="DT_NDI_TS")
    return common.build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def get_occurrence(project_id, occurrence_id):
    """
    Returns the requested &#x60;Note&#x60;.

    :param project_id: First part of occurrence &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: projects/{project_id}/notes/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiOccurrence
    """

    db = common.get_db()
    auth_client = common.get_auth_client()
    subject = auth_util.get_subject(connexion.request)
    if not auth_client.can_read_occurrence(subject):
        return common.build_error(HTTPStatus.UNAUTHORIZED, "Not allowed to get occurrences: {}".format(subject))

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(subject.account_id, project_id, occurrence_id)
        doc = db.get_doc(occurrence_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_doc_id))


def delete_occurrence(project_id, occurrence_id):
    """
    Deletes the given &#x60;Note&#x60; from the system.

    :param project_id: First part of occurrence &#x60;name&#x60;: projects/{project_id}/occurrences/{occurrence_id}
    :type project_id: str
    :param occurrence_id: Second part of occurrence &#x60;name&#x60;: projects/{project_id}/occurrences/{occurrence_id}
    :type occurrence_id: str

    :rtype: ApiEmpty
    """

    db = common.get_db()
    auth_client = common.get_auth_client()
    subject = auth_util.get_subject(connexion.request)
    if not auth_client.can_delete_occurrence(subject):
        return common.build_error(HTTPStatus.UNAUTHORIZED, "Not allowed to delete occurrences: {}".format(subject))

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(subject.account_id, project_id, occurrence_id)
        doc = db.delete_doc(occurrence_doc_id)
        return common.build_result(HTTPStatus.OK, {})
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_doc_id))


def _set_occurrence_defaults(doc, note):
    if 'short_description' not in doc:
        doc['short_description'] = note.get('short_description')
    if 'long_description' not in doc:
        doc['long_description'] = note.get('long_description')
    if 'reported_by' not in doc:
        doc['reported_by'] = note.get('reported_by')

    kind = doc['kind']
    if kind == 'FINDING':
        merged_finding = dict_util.dict_merge(note['finding'], doc['finding'])
        doc['finding'] = merged_finding
    elif kind == 'KPI':
        merged_kpi = dict_util.dict_merge(note['kpi'], doc['kpi'])
        doc['kpi'] = merged_kpi


def _set_internal_occurrence_severity(doc):
    kind = doc['kind']
    if kind == 'FINDING':
        details = doc['finding']
    else:
        return

    severity = details.get('severity', 'medium')
    severity_lower = severity.lower()
    if severity_lower not in ['low', 'medium', 'high']:
        raise ValueError("Invalid severity value: '{}'. Valid values are LOW, MEDIUM, and HIGH.".format(severity))

    details['severity'] = _INTERNAL_LEVEL_MAP[severity_lower]

    # only findings have certainty
    certainty = details.get('certainty')
    if certainty is not None:
        certainty_lower = certainty.lower()
        if certainty_lower not in ['low', 'medium', 'high']:
            raise ValueError("Invalid certainty value: '{}'. Valid values are LOW, MEDIUM, and HIGH.".format(certainty))
        details['certainty'] = _INTERNAL_LEVEL_MAP[certainty_lower]


def _set_external_occurrence_severity(occurrence):
    kind = occurrence['kind']
    if kind == 'FINDING':
        details = occurrence['finding']
    else:
        return

    severity = details['severity']
    details['severity'] = _EXTERNAL_LEVEL_MAP[severity]

    certainty = details.get('certainty')
    if certainty is not None:
        details['certainty'] = _EXTERNAL_LEVEL_MAP[certainty]


_INTERNAL_LEVEL_MAP = {
    'low': 1,
    'medium': 2,
    'high': 3
}


_EXTERNAL_LEVEL_MAP = {
    1: 'low',
    2: 'medium',
    3: 'high'
}


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    doc.pop('account_id', None)

    # externalize the security value
    _set_external_occurrence_severity(doc)
    return doc


def _week_date_iso_format(iso_calendar):
    return "{:04d}-W{:02d}-{}".format(iso_calendar[0], iso_calendar[1], iso_calendar[2])