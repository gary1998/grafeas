import json
from controllers import common

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


def backup_all(db, filename):
    with open(filename, 'w') as f:
        for doc in db.all_docs():
            f.write(json.dumps(doc) + '\n')


def get_occurrences_of_notes(db, note_doc_ids):
    return db.find(
        filter_={
            'context.account_id': USER_ACCOUNT_ID,
            'doc_type': 'Occurrence',
            'kind': 'FINDING',
            'note_doc_id': note_doc_ids
        },
        index="RAI_DT_K_TS_NDI",
        sort=[
            {'context.account_id': 'desc'},
            {'doc_type': 'desc'},
            {'kind': 'desc'},
            {'update_timestamp': 'desc'}
        ],
        fields=['_id', 'update_time'])


def delete_occurrences(docs):
    n = 1
    for doc in docs:
        occurrence_doc_id = doc['_id']
        update_time = doc['update_time']
        print("Deleting occurrence #{}: {} - {}".format(n, occurrence_doc_id, update_time))
        db.delete_doc(occurrence_doc_id)
        n += 1


db = common.get_db()
#backup_all(db, "grafeas-backup")

suspicious_server_findings = get_occurrences_of_notes(db, SUSPICIOUS_SERVERS_NOTES_IDS)
print("Deleting all suspicious server findings: {}".format(len(suspicious_server_findings)))
input("Press Enter to continue...")
delete_occurrences(suspicious_server_findings)
print("Done!")

suspicious_client_findings = get_occurrences_of_notes(db, SUSPICIOUS_CLIENTS_NOTES_IDS)
findings_to_delete = suspicious_client_findings[80:]
print("Deleting suspicious clients findings: {} of {}".format(
    len(findings_to_delete), len(suspicious_client_findings)))
input("Press Enter to continue...")
delete_occurrences(findings_to_delete)
print("Done!")
