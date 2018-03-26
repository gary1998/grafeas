import connexion
import http
import logging
from controllers import api
from controllers import auth
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.account_data")


def delete_account(account_id):
    """
    Deletes all the subject's data

    :rtype: ApiEmpty
    """
    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.get_subject(connexion.request)
        auth_client.assert_can_delete_occurrences(subject)

        if account_id != subject.account_id:
            auth_client.assert_can_delete_occurrences_for_others(subject)
        else:
            auth_client.assert_can_delete_occurrences(subject)

        api_impl = api.get_api_impl()
        api_impl.delete_account_occurrences(account_id)

        account_deleted_occurrence = {
            "id": "account-deleted-{}".format(account_id),
            "note_name": "system/projects/core/notes/account_deleted",
            "kind": "ACCOUNT_DELETED",
            "context": {
                "account_id": account_id
            }
        }

        occurrence_id = account_deleted_occurrence['id']
        api_impl.write_occurrence(subject.account_id, 'core', occurrence_id, account_deleted_occurrence)
        logger.info("Data deleted for account: {}".format(account_id))
        return common.build_result(http.HTTPStatus.OK, {})
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting account data")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while deleting account data")
        raise