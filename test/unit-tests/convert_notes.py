
import os
from util import cloudant_client


def init_db():
    db = cloudant_client.CloudantDatabase(
        os.environ['GRAFEAS_URL'],
        'grafeas',
        os.environ['GRAFEAS_USERNAME'],
        os.environ['GRAFEAS_PASSWORD'])
    print("DB initialized.")
    return db


def covert_notes():
    db = init_db()

    result = db.find(key_values={'doc_type': 'Note'}, index="ALL_FIELDS")
    for doc in result.docs:
        doc['context'] = {"account_id": doc['account_id']}
        db.update_doc(doc['_id'], doc)


covert_notes()