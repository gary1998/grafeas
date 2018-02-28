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
    account_id = auth_util.get_account_id(connexion.request)
    replace_if_exists_header_value = connexion.request.headers.get('Replace-If-Exists')
    replace_if_exists = replace_if_exists_header_value is not None and replace_if_exists_header_value.lower() == 'true'
    project_doc_id = common.build_project_doc_id(account_id, project_id)

    if 'id' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Missing required field: 'id'")

    occurrence_id = body['id']
    occurrence_name = common.build_occurrence_name(project_id, occurrence_id)

    if 'note_name' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Missing required field: 'note_name'")

    note_name = body['note_name']

    # get the occurrence's note
    try:
        note_doc_id = "{}/{}".format(account_id, note_name)
        note = db.get_doc(note_doc_id)
    except exceptions.NotFoundError:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Note not found: {}".format(note_name))

    if 'kind' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Missing required field: 'kind'")

    kind = body['kind']

    if kind not in ['FINDING', 'KPI']:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Invalid 'kind' value, only 'FINDING' and 'KPI' are allowed")

    if kind == 'FINDING' and 'finding' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Missing field for 'FINDING' occurrence: 'finding'")
    if kind == 'KPI' and 'kpi' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Missing field for 'KPI' occurrence: 'kpi'")

    if 'context' not in body:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Missing required field: 'context'")

    context = body['context']

    if 'account_id' not in context:
        return common.build_error(
            HTTPStatus.BAD_REQUEST,
            "Missing required field: 'context.account_id'")

    body['doc_type'] = 'Occurrence'
    body['account_id'] = account_id
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

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(account_id, project_id, occurrence_id)
        db.create_doc(occurrence_doc_id, body)
        return common.build_result(HTTPStatus.OK, _clean_doc(body))
    except exceptions.AlreadyExistsError:
        if replace_if_exists:
            return update_occurrence(project_id, occurrence_id, body)
        else:
            return common.build_error(HTTPStatus.CONFLICT, "Occurrence already exists: {}".format(occurrence_doc_id))


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
    account_id = auth_util.get_account_id(connexion.request)
    project_doc_id = common.build_project_doc_id(account_id, project_id)

    docs = db.find(
        filter_={
            'doc_type': 'Occurrence',
            'project_doc_id': project_doc_id
        },
        index="DT_PDI")
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
    account_id = auth_util.get_account_id(connexion.request)

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(account_id, project_id, occurrence_id)
        doc = db.get_doc(occurrence_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_doc_id))


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
    account_id = auth_util.get_account_id(connexion.request)

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

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(account_id, project_id, occurrence_id)
        doc = db.update_doc(occurrence_doc_id, body)
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
    account_id = auth_util.get_account_id(connexion.request)

    try:
        occurrence_doc_id = common.build_occurrence_doc_id(account_id, project_id, occurrence_id)
        doc = db.delete_doc(occurrence_doc_id)
        return common.build_result(HTTPStatus.OK, _clean_doc(doc))
    except exceptions.NotFoundError:
        return common.build_error(HTTPStatus.NOT_FOUND, "Occurrence not found: {}".format(occurrence_doc_id))


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
    account_id = auth_util.get_account_id(connexion.request)
    note_doc_id = common.build_note_doc_id(account_id, project_id, note_id)

    docs = db.find(
        filter_={
            'doc_type': 'Occurrence',
            'note_doc_id': note_doc_id
        },
        index="DT_NDI")
    return common.build_result(HTTPStatus.OK, [_clean_doc(doc) for doc in docs])


def _set_occurrence_defaults(occurrence, note):
    if 'short_description' not in occurrence:
        occurrence['short_description'] = note.get('short_description')
    if 'long_description' not in occurrence:
        occurrence['long_description'] = note.get('long_description')
    if 'reported_by' not in occurrence:
        occurrence['reported_by'] = note.get('reported_by')

    if occurrence['kind'] == 'FINDING':
        merged_finding = dict_util.dict_merge(note['finding'], occurrence['finding'])
        occurrence['finding'] = merged_finding


def _clean_doc(doc):
    doc.pop('_id', None)
    doc.pop('_rev', None)
    doc.pop('doc_type', None)
    doc.pop('account_id', None)
    return doc


def _week_date_iso_format(iso_calendar):
    return "{:04d}-W{:02d}-{}".format(iso_calendar[0], iso_calendar[1], iso_calendar[2])