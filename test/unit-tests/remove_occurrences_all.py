import json
import os
from util import cloudant_client

NOTE_ACCOUNT_ID='0ce28a8d963f13ef436b3f12f71d213a'
USER_ACCOUNT_ID='697e84fcca45c9439aae525d31ef1a27'

SUSPICIOUS_CLIENTS_NOTES_IDS=[
    "0ce28a8d963f13ef436b3f12f71d213a/projects/security-advisor/notes/xforce-anonym_client",
    "0ce28a8d963f13ef436b3f12f71d213a/projects/security-advisor/notes/xforce-bot_client",
    "0ce28a8d963f13ef436b3f12f71d213a/projects/security-advisor/notes/xforce-malware_client",
    "0ce28a8d963f13ef436b3f12f71d213a/projects/security-advisor/notes/xforce-scanner_client"
]

SUSPICIOUS_SERVERS_NOTES_IDS=[
    "0ce28a8d963f13ef436b3f12f71d213a/projects/security-advisor/notes/xforce-anonym_server",
    "0ce28a8d963f13ef436b3f12f71d213a/projects/security-advisor/notes/xforce-bot_server",
    "0ce28a8d963f13ef436b3f12f71d213a/projects/security-advisor/notes/xforce-malware_server",
    "0ce28a8d963f13ef436b3f12f71d213a/projects/security-advisor/notes/xforce-scanner_server"
]


def init_db():
    db = cloudant_client.CloudantDatabase(
        os.environ['GRAFEAS_URL'],
        os.environ['GRAFEAS_DB_NAME'],
        os.environ['GRAFEAS_USERNAME'],
        os.environ['GRAFEAS_PASSWORD'])
    print("DB initialized.")
    return db


def backup_all(filename):
    db = init_db()

    n = 1
    skip = 0
    limit = 1000

    with open(filename, 'w') as f:
        while True:
            docs = db.all_docs(include_docs=True, skip=skip, limit=limit)
            for doc in docs:
                f.write(json.dumps(doc) + '\n')
                n += 1

            if len(docs) < limit:
                break
            skip += limit
            print("{} docs backup up".format(skip))

    print("{} total docs backup up".format(n))


def delete_all_findings_before_date(date):
    db = init_db()
    date = date[:10] # truncate date to first 10 chars (only iso date chars)

    deleted_count = 0
    handled_count = 0
    skip = 0
    limit = 1000

    while True:
        try:
            docs = db.all_docs(include_docs=True, skip=skip, limit=limit)
            for doc in docs:
                handled_count += 1

                doc = doc['doc']
                if doc.get('doc_type') != 'Occurrence':
                    continue

                if doc.get('kind') != 'FINDING':
                    continue

                update_time = doc['update_time']
                update_date = update_time[:10]
                if update_date < date:
                    doc_id = doc['_id']
                    print("Deleting {} #{}: {} ({})".format(doc['kind'], handled_count, doc_id, update_time))
                    db.delete_doc(doc_id)
                    deleted_count += 1

            if len(docs) < limit:
                break
            skip += limit
            print("{} findings handled".format(handled_count))
        except Exception as e:
            print("An unexpected error was encountered while deleting findings: {}".format(str(e)))
            print("Re-initializing DB ...")
            db = init_db()
            skip = handled_count

    print("{} total findings deleted".format(deleted_count))


def delete_findings_of_notes(note_full_names):
    db = init_db()

    docs = db.find(
        filter_={
            'context.account_id': USER_ACCOUNT_ID,
            'doc_type': 'Occurrence',
            'kind': 'FINDING',
            'note_doc_id': note_full_names
        },
        index="RAI_DT_K_TS_NDI",
        sort=[
            {'context.account_id': 'desc'},
            {'doc_type': 'desc'},
            {'kind': 'desc'},
            {'update_timestamp': 'desc'}
        ],
        fields=['_id', 'update_time'])

    _delete_occurrences(db, docs)


def _delete_occurrences(db, docs):
    n = 1
    for doc in docs:
        occurrence_full_name = doc['_id']
        update_time = doc['update_time']
        print("Deleting occurrence #{}: {} ({})".format(n, occurrence_full_name, update_time))
        db.delete_doc(occurrence_full_name)
        n += 1

#backup_all(db, "grafeas-backup-stage1")
delete_all_findings_before_date('2018-05-14')

'''
delete_findings_of_notes(SUSPICIOUS_SERVERS_NOTES_IDS)
dekete_findings_of_notes(SUSPICIOUS_CLIENTS_NOTES_IDS)
print("Done!")
'''

