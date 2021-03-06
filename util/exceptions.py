# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
'''
Created on Mar 13, 2017

@author: alberto
'''

from http import HTTPStatus


class JSONError(Exception):
    """
        A problem details object has the following members:

        . "type" (string) - A URI reference [RFC3986] that identifies the problem type.
          This specification encourages that, when dereferenced,
          it provide human-readable documentation for the problem type (e.g., using HTML [W3C.REC-html5-20141028]).
          When this member is not present, its value is assumed to be "about:blank".

        . "title" (string) - A short, human-readable summary of the problem type.
          It SHOULD NOT change from occurrence to occurrence of the problem, except for purposes of localization
          (e.g., using proactive content negotiation; see [RFC7231], Section 3.4).

        . "status" (number) - The HTTP status code ([RFC7231], Section 6)
          generated by the origin server for this occurrence of the problem.

        . "detail" (string) - A human-readable explanation specific to this occurrence of the problem.

        . "instance" (string) - A URI reference that identifies the specific occurrence of the problem.
          It may or may not yield further information if dereferenced.
    """

    def __init__(self,  detail: str, status: int, title: str=None, instance: str=None, type_:str=None):
        super().__init__(detail)
        self.detail = detail
        self.status = status
        self.title = title
        self.instance = instance
        self.type = type_

    @staticmethod
    def from_http_status(http_status, detail: str=None, title: str=None, instance: str=None):
        return JSONError(
            detail if detail else http_status.description,
            http_status.value,
            title if title else http_status.phrase,
            instance)

    @staticmethod
    def from_http_status_code(http_status_code, detail: str=None, title: str=None, instance: str=None):
        http_status = HTTP_STATUS_CODE_HTTP_STATUS_MAP.get(http_status_code)
        if http_status is not None:
            return JSONError.from_http_status(http_status, detail, title, instance)

        return JSONError("HTTP Error", http_status_code, title, instance)

    def to_error(self):
        error = {
            "detail": self.detail,
            "status": self.status
        }

        if self.title:
            error['title'] = self.title

        if self.instance:
            error['instance'] = self.instance

        if self.type:
            error['type'] = self.type
        else:
            error['type'] = "about:blank"

        return error, self.status


class AlreadyExistsError(JSONError):
    def __init__(self, detail: str, instance: str=None):
        super().__init__(
            detail,
            HTTPStatus.CONFLICT.value, HTTPStatus.CONFLICT.phrase,
            instance)


class NotFoundError(JSONError):
    def __init__(self, detail: str, instance: str=None):
        super().__init__(
            detail,
            HTTPStatus.NOT_FOUND.value, HTTPStatus.NOT_FOUND.phrase,
            instance)


class BadRequestError(JSONError):
    def __init__(self, detail: str, instance: str=None):
        super().__init__(
            detail,
            HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase,
            instance)


class InternalServerError(JSONError):
    def __init__(self, detail: str, instance: str=None):
        super().__init__(
            detail,
            HTTPStatus.INTERNAL_SERVER_ERROR.value, HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
            instance)


class ForbiddenError(JSONError):
    def __init__(self, detail: str, instance: str=None):
        super().__init__(
            detail,
            HTTPStatus.FORBIDDEN.value, HTTPStatus.FORBIDDEN.phrase,
            instance)


class UnauthorizedError(JSONError):
    def __init__(self, detail: str, instance: str=None):
        super().__init__(
            detail,
            HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase,
            instance)


class UnprocessableEntity(JSONError):
    def __init__(self, detail: str, instance: str=None):
        super().__init__(
            detail,
            HTTPStatus.UNPROCESSABLE_ENTITY.value, HTTPStatus.UNPROCESSABLE_ENTITY.phrase,
            instance)


HTTP_STATUS_CODE_HTTP_STATUS_MAP = {
    100: HTTPStatus.CONTINUE,
    101: HTTPStatus.SWITCHING_PROTOCOLS,
    102: HTTPStatus.PROCESSING,
    200: HTTPStatus.OK,
    201: HTTPStatus.CREATED,
    202: HTTPStatus.ACCEPTED,
    203: HTTPStatus.NON_AUTHORITATIVE_INFORMATION,
    204: HTTPStatus.NO_CONTENT,
    205: HTTPStatus.RESET_CONTENT,
    206: HTTPStatus.PARTIAL_CONTENT,
    207: HTTPStatus.MULTI_STATUS,
    208: HTTPStatus.ALREADY_REPORTED,
    226: HTTPStatus.IM_USED,
    300: HTTPStatus.MULTIPLE_CHOICES,
    301: HTTPStatus.MOVED_PERMANENTLY,
    302: HTTPStatus.FOUND,
    303: HTTPStatus.SEE_OTHER,
    304: HTTPStatus.NOT_MODIFIED,
    305: HTTPStatus.USE_PROXY,
    307: HTTPStatus.TEMPORARY_REDIRECT,
    308: HTTPStatus.PERMANENT_REDIRECT,
    400: HTTPStatus.BAD_REQUEST,
    401: HTTPStatus.UNAUTHORIZED,
    402: HTTPStatus.PAYMENT_REQUIRED,
    403: HTTPStatus.FORBIDDEN,
    404: HTTPStatus.NOT_FOUND,
    405: HTTPStatus.METHOD_NOT_ALLOWED,
    406: HTTPStatus.NOT_ACCEPTABLE,
    407: HTTPStatus.PROXY_AUTHENTICATION_REQUIRED,
    408: HTTPStatus.REQUEST_TIMEOUT,
    409: HTTPStatus.CONFLICT,
    410: HTTPStatus.GONE,
    411: HTTPStatus.LENGTH_REQUIRED,
    412: HTTPStatus.PRECONDITION_FAILED,
    413: HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
    414: HTTPStatus.REQUEST_URI_TOO_LONG,
    415: HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
    417: HTTPStatus.EXPECTATION_FAILED,
    422: HTTPStatus.UNPROCESSABLE_ENTITY,
    423: HTTPStatus.LOCKED,
    424: HTTPStatus.FAILED_DEPENDENCY,
    426: HTTPStatus.UPGRADE_REQUIRED,
    428: HTTPStatus.PRECONDITION_REQUIRED,
    429: HTTPStatus.TOO_MANY_REQUESTS,
    431: HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
    500: HTTPStatus.INTERNAL_SERVER_ERROR,
    501: HTTPStatus.NOT_IMPLEMENTED,
    502: HTTPStatus.BAD_GATEWAY,
    503: HTTPStatus.SERVICE_UNAVAILABLE,
    504: HTTPStatus.GATEWAY_TIMEOUT,
    505: HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
    506: HTTPStatus.VARIANT_ALSO_NEGOTIATES,
    507: HTTPStatus.INSUFFICIENT_STORAGE,
    508: HTTPStatus.LOOP_DETECTED,
    510: HTTPStatus.NOT_EXTENDED,
    511: HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED
}
