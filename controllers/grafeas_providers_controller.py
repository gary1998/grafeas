import connexion
import http
import logging
from controllers import api
from controllers import auth
from controllers import common
from util import exceptions


logger = logging.getLogger("grafeas.providers")


def list_providers(account_id, filter=None, page_size=None, page_token=None):
    """
    Lists &#x60;Providers&#x60;

    :param filter: The filter expression.
    :type filter: str
    :param page_size: Number of providers to return in the list.
    :type page_size: int
    :param page_token: Token to provide to skip to a particular spot in the list.
    :type page_token: str

    :rtype: ApiListProvidersResponse
    """

    try:
        auth_client = auth.get_auth_client()
        subject = auth_client.assert_can_read_providers(connexion.request, account_id)

        api_impl = api.get_api_impl()
        result = api_impl.list_providers(subject, account_id, filter, page_size, page_token)
        return common.build_result(
            http.HTTPStatus.OK,
            {
                "providers": result.docs,
                "next_page_token": result.bookmark
            })
    except exceptions.JSONError as e:
        logger.exception("An error was encountered while listing providers")
        return e.to_error()
    except Exception as e:
        logger.exception("An unexpected error was encountered while listing providers")
        return exceptions.InternalServerError(str(e)).to_error()

