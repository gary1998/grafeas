import connexion
import http
import logging
from controllers import api
from controllers import auth
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.account_data")


def delete_account_data(account_id, start_time=None, end_time=None):
    """
    Deletes all the subject's data

    :rtype: ApiEmpty
    """
    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_delete_occurrences(connexion.request, account_id)

        api_impl = api.get_api_impl()
        api_impl.delete_account_occurrences(subject, account_id, start_time, end_time)

        account_deleted_occurrence = {
            "id": "account-deleted-{}".format(account_id),
            "note_name": "system/providers/core/notes/account_deleted",
            "kind": "ACCOUNT_DELETED",
            "context": {
                "account_id": account_id
            }
        }

        occurrence_id = account_deleted_occurrence['id']
        api_impl.write_occurrence(subject, account_id, 'core', occurrence_id, account_deleted_occurrence)
        logger.debug("Data deleted for account: {} in time range start {} end {}".format(account_id, start_time, end_time))
        return common.build_result(http.HTTPStatus.OK, {})
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting account data")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while deleting account data")
        raise