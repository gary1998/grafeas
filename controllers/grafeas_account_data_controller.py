import connexion
import http
import logging
from controllers import api
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.account_data")


def delete_account_data():
    """
    Deletes all the subject's data

    :rtype: ApiEmpty
    """
    try:
        api_impl = api.get_api_impl()
        api_impl.delete_all_account_data(connexion.request)
        return common.build_result(http.HTTPStatus.OK, {})
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while deleting all account data")
        return e.to_error()
    except:
        logger.exception("An unexpected error was encountered while deleting all account data")
        raise