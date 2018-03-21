import connexion
from cloudant.error import CloudantDatabaseException
from http import HTTPStatus
import logging
from . import common
from util import auth_util


logger = logging.getLogger("grafeas.account_data")


def delete_account_data():
    try:
        db = common.get_db()
        auth_client = common.get_auth_client()

        try:
            subject = auth_util.get_subject(connexion.request)
            if not auth_client.can_write_note(subject):
                return common.build_error(
                    HTTPStatus.FORBIDDEN,
                    "Not allowed to create notes: {}".format(subject),
                    logger)
        except Exception as e:
            return common.build_error(HTTPStatus.UNAUTHORIZED, str(e), logger)

        docs = db.find(
            filter_={
                'context.account_id': subject.account_id,
                'doc_type': 'Occurrence'
            },
            index="RAI_DT",
            fields=['_id'])

        for doc in docs:
            occurrence_doc_id = doc['_id']
            db.delete_doc(occurrence_doc_id)

    except CloudantDatabaseException as e:
        return common.build_error(
            e.status_code,
            "An unexpected DB error was encountered: {}".format(str(e)), logger)
    except:
        logger.exception("An unexpected error was encountered while deleting account data")
        raise