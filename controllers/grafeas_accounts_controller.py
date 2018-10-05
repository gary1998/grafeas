# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import connexion
import http
import logging
from controllers import api
from controllers import auth
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.account_data")


def delete_account_data(account_id, start_time=None, end_time=None, count=None):
    """
    Deletes all the subject's data

    :rtype: ApiEmpty
    """
    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_delete_occurrences(
            connexion.request, account_id)

        api_impl = api.get_api_impl()
        deleted_count = api_impl.delete_account_occurrences(
            subject, account_id, start_time, end_time, count)

        # All account data will be deleted if there are no restrictions on time and count
        # Only in that case create this occurrence
        if start_time is None and end_time is None and count is None:
            account_deleted_occurrence = {
                "id": "account-deleted-{}".format(account_id),
                "note_name": "system/providers/core/notes/account_deleted",
                "kind": "ACCOUNT_DELETED",
                "context": {
                    "account_id": account_id
                }
            }

            occurrence_id = account_deleted_occurrence['id']
            api_impl.write_occurrence(
                subject, account_id, 'core', occurrence_id, account_deleted_occurrence)
        logger.debug("Data deleted for account: {} in time range start {} end {} and count {}".format(
            account_id, start_time, end_time, count))
        return common.build_result(http.HTTPStatus.OK, {'deleted_count': deleted_count})
    except exceptions.JSONError as e:
        logger.exception(
            "An error was encountered while deleting account data")
        return e.to_error()
    except:
        logger.exception(
            "An unexpected error was encountered while deleting account data")
        raise
