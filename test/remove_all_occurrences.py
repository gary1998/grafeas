from controllers import common

db = common.get_db()
ACCOUNT_ID='d0c8a917589e40076961f56b23056d16'
PROJECT_ID='security-advisor'
PROJECT_DOC_ID = common.build_project_doc_id(ACCOUNT_ID, PROJECT_ID)

docs = db.find(
    filter_={
        'doc_type': 'Occurrence',
        'project_doc_id': PROJECT_DOC_ID
    },
    index="DT_PDI_TS")

n = 1
for doc in docs:
    occurrence_doc_id = doc['_id']
    update_time = doc['update_time']
    print("Deleting occurrence #{}: {} - {}".format(n, occurrence_doc_id, update_time))
    doc = db.delete_doc(occurrence_doc_id)
    n += 1
