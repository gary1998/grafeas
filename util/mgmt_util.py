import json
import os
from util import cloudant_client


def init_db():
    db = cloudant_client.CloudantDatabase(
        os.environ['GRAFEAS_URL'],
        os.environ.get('GRAFEAS_DB_NAME', "grafeas"),
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


def delete_docs_before_date(doc_type, kind, date):
    db = init_db()
    date = date[:10] # truncate date to first 10 chars (only iso date chars)
    bookmark = None
    limit = 200
    total_deleted_count = 0

    while True:
        try:
            deleted_docs = []
            result = db.find(
                key_values={
                    'doc_type': doc_type,
                    'kind': kind
                },
                index='ALL_FIELDS',
                fields=['_id', '_rev', 'update_time'],
                limit=limit, bookmark=bookmark)
            for doc in result.docs:
                update_time = doc['update_time']
                update_date = update_time[:10]
                if update_date < date:
                    deleted_doc = {
                        '_deleted': True,
                        '_id': doc['_id'],
                        '_rev': doc['_rev']
                    }
                    deleted_docs.append(deleted_doc)

            if deleted_docs:
                db.db.bulk_docs(deleted_docs)

            if len(result.docs) < limit:
                break

            bookmark = result.bookmark
            total_deleted_count += len(deleted_docs)
            print("{} docs deleted".format(total_deleted_count))
        except Exception as e:
            print("An unexpected error was encountered while deleting docs: {}".format(str(e)))
            print("Re-initializing DB ...")
            db = init_db()
            bookmark = None

    print("{} total docs deleted".format(total_deleted_count))


def get_distinct_accounts(doc_type):
    db = init_db()
    bookmark = None
    limit = 200
    distinct_accounts = set()

    while True:
        result = db.find(
            key_values={
                'doc_type': doc_type
            },
            index='ALL_FIELDS',
            fields=['context.account_id'],
            limit=limit, bookmark=bookmark)

        for doc in result.docs:
            distinct_accounts.add(doc['context']['account_id'])

        if len(result.docs) < limit:
            break

        bookmark = result.bookmark

    print("{} total distinct accounts".format(len(distinct_accounts)))


def convert_notes():
    db = init_db()
    limit = 200
    bookmark = None

    while True:
        result = db.find(
            key_values={'doc_type': 'Note'},
            index="ALL_FIELDS",
            limit=limit,
            bookmark=bookmark)

        for doc in result.docs:
            doc['context'] = {"account_id": doc['account_id']}
            db.update_doc(doc['_id'], doc)

        if len(result.docs) < limit:
            break

        bookmark = result.bookmark


'''
delete_docs_before_date('Occurrence', 'FINDING', '2018-06-04')
'''

get_distinct_accounts('Occurrence')
