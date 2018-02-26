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
    db.create_query_index("DT_NDI", ['doc_type', 'note_doc_id', 'update_timestamp'])
    db.create_query_index("DT_CAI_PDI", ['doc_type', 'context.account_id', 'update_timestamp', 'project_doc_id'])
    db.create_query_index("DT_CAI_NDI", ['doc_type', 'context.account_id', 'update_timestamp', 'note_doc_id'])

    # 2018-04-15T16:30:00
    db.add_view(
        'time_series',
        'finding_count_by_date_time',
        """
        function(doc) {{
            if (doc.doc_type == "Occurrence" && doc.kind == 'FINDING') {{
                emit([doc.context.account_id, doc.note_doc_id, 
                    parseInt(doc.update_time.substring(0, 4), 10),
                    parseInt(doc.update_time.substring(5, 7), 10), 
                    parseInt(doc.update_time.substring(8, 10), 10),
                    parseInt(doc.update_time.substring(11, 13), 10),
                    parseInt(doc.update_time.substring(14, 16), 10),
                    parseInt(doc.update_time.substring(17, 19), 10)],
                    1);
            }}
        }}
        """,
        '_sum')

    # 2018-W04-2
    db.add_view(
        'time_series',
        'finding_count_by_week_date',
        """
        function(doc) {{
            if (doc.doc_type == "Occurrence" && doc.kind == 'FINDING') {{
                emit([doc.context.account_id, doc.note_doc_id, 
                    parseInt(doc.update_week_date.substring(0, 4), 10),
                    parseInt(doc.update_week_date.substring(6, 8), 10),
                    parseInt(doc.update_week_date.substring(9, 10), 10)],
                    1);
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
