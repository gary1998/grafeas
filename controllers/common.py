import os
import threading
from util.cloudant_client import CloudantDatabase


__db = None
__db_lock = threading.Lock()


def get_db():
    """
    Opens a new db connection if there is none yet for the current application context.
    """

    global __db
    with __db_lock:
        if __db is None:
            __db = __create_db()

        return __db


def build_result(status, data):
    return data, status.value


def build_error(status, detail):
    error = {
        "detail": detail,
        "status": status.value,
        "title": status.description,
        "type": "about:blank"
    }
    return error, status.value


def __create_db():
    db = CloudantDatabase(
        os.environ['GRAFEAS_URL'],
        os.environ['GRAFEAS_DB_NAME'],
        os.environ['GRAFEAS_USERNAME'],
        os.environ['GRAFEAS_PASSWORD'])

    db.create_query_index("DT_OAI", ['doc_type', 'account_id', 'update_timestamp'])
    db.create_query_index("DT_PDI", ['doc_type', 'project_doc_id', 'update_timestamp'])
    db.create_query_index("DT_CAI_PDI", ['doc_type', 'context.account_id', 'project_doc_id', 'update_timestamp'])
    db.create_query_index("DT_NDI", ['doc_type', 'note_doc_id', 'update_timestamp'])
    db.create_query_index("DT_CAI_NDI", ['doc_type', 'context.account_id', 'note_doc_id', 'update_timestamp'])

    db.add_view(
        'time_series',
        'finding_count_by_date_time',
        """
        function(doc) {{
            if (doc.doc_type == "Occurrence" && doc.kind == 'FINDING') {{
                emit([doc.context.account_id, doc.note_doc_id, 
                      doc.update_time.substring(0, 4), doc.update_time.substring(5, 7), 
                      doc.update_time.substring(8, 10), doc.update_time.substring(11, 13),
                      doc.update_time.substring(14, 16), doc.update_time.substring(17, 19)], 1);
            }}
        }}
        """,
        '_sum')

    db.add_view(
        'time_series',
        'finding_count_by_week_date',
        """
        function(doc) {{
            if (doc.doc_type == "Occurrence" && doc.kind == 'FINDING') {{
                emit([doc.context.account_id, doc.note_doc_id, doc.update_week_date.substring(0, 4),
                      doc.update_week_date.substring(6, 8), doc.update_week_date.substring(9, 10)], 1);
            }}
        }}
        """,
        '_sum')

    return db


def build_project_name(project_id):
    return "projects/{}".format(project_id)


def build_project_doc_id(account_id, project_id):
    return "{}/projects/{}".format(account_id, project_id)


def build_note_name(project_id, note_id):
    return "projects/{}/notes/{}".format(project_id, note_id)


def build_note_doc_id(account_id, project_id, note_id):
    return "{}/projects/{}/notes/{}".format(account_id, project_id, note_id)


def build_occurrence_name(project_id, occurrence_id):
    return "projects/{}/occurrences/{}".format(project_id, occurrence_id)


def build_occurrence_doc_id(account_id, project_id, occurrence_id):
    return "{}/projects/{}/occurrences/{}".format(account_id, project_id, occurrence_id)
