import jwt
import logging
from time import time
from base64 import b64decode
from Crypto.Util.number import bytes_to_long
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from pepclient.crn import create, parse
import requests


# ---------------------------------------------------------------------
# Default iam production
iam_urls = [
    'https://iam-api.ng.bluemix.net'
]
# ---------------------------------------------------------------------

API_KEY_LEEWAY = 2


class TokenClient(object):

    def __init__(self, iam_endpoint=iam_urls, logger=None):
        """
        Client to validate IAM tokens
        :param iam_endpoint: List of supported endpoints from where to obtain
        public keys to validate IAM tokens
        :param logger: logger instance
        :return:
        """
        self.logger = logger or logging.getLogger(__name__)
        self.public_keys = {}
        self.iam_endpoint = []
        if isinstance(iam_endpoint, list):
            for endpoint in iam_urls:
                self.iam_endpoint.append(endpoint)
        else:
            self.iam_endpoint.append(iam_endpoint)

    def validate_parse_token(self, token):
        """
         Validate and parse token, on success return an object with token
         fields: subject (username) and issuer.
        :param token: apikey or IAM token
        :return: on success, object with fields: subject (username),
        issuer (IAM service that issue the token), else raise exception
        (ValueError, AssertionError, RuntimeError)
        """
        parsed_token = self.validate_token(token)
        result_object = {
            'subject': parsed_token['sub'],
            'issuer': parsed_token['iss']
        }
        return result_object

    def getSubjectAsIamIdClaim(self, token):
        """
        Processes a jwk token (string) and returns a "Subject" object which
        contains a iamId or attributes object
        """
        if token is None:
            raise ValueError('Parameter token is empty or invalid')

        parsed_token = self.validate_token(token)

        if parsed_token is None:
            raise ValueError('Failed to get claim from token, invalid token')

        try:
            tokenSub = parsed_token['iam_id']
            subType = parsed_token['sub_type']
        except:
            subType = None

        if tokenSub is None:
            raise ValueError('Failed to get IamId claim from token,'
                             'invalid token')

        if subType is None:
            result_object = {
                'subject': {
                    'iamId': {
                        'userId': tokenSub
                    }
                }
            }
        else:
            if subType == 'ServiceId':
                result_object = {
                    'subject': {
                        'iamId': {
                            'serviceId': tokenSub
                        }
                    }
                }
            elif subType == 'CRN':
                result_object = {
                    'subject': {
                        'attributes': parse(tokenSub)
                    }
                }
            else:
                result_object = {}

        return result_object

    def validate_token(self, token):
        """
        Validate apikey or IAM token locally, using Json web key set
        :param token: apikey or IAM token
        :return on success, else raise exception (ValueError, AssertionError,
        RuntimeError)
        """
        if token is None:
            raise ValueError('Parameter token is empty or invalid')

        token = self._strip_prefix('bearer ', token)
        token = self._strip_prefix('Bearer ', token)

        try:
            kid = jwt.get_unverified_header(token)['kid']
        except:
            raise ValueError('Parameter token is invalid')

        key = self._get_public_key(kid)
        if not key:
            raise AssertionError('UNAUTHORIZED')

        try:
            decoded_token = jwt.decode(
                token, key['public_key'], algorithms=key['alg'], options={
                    'verify_aud': False,
                    'verify_iss': False,   # We do our own checking below
                    'verify_iat': False},  # We do our own checking below.,
                leeway=API_KEY_LEEWAY)
        except:
            raise AssertionError('UNAUTHORIZED')

        # Check iat.
        self._validate_iat(decoded_token)

        # Validate issuer
        self._validate_iss(decoded_token)

        return decoded_token

    def _get_public_key(self, kid):
        if kid not in self.public_keys:
            self._update_public_keys()
        if not self.public_keys:
            raise RuntimeError('List of public keys is empty')

        return self.public_keys.get(kid)

    def _update_public_keys(self):
        """
        Update Json web key set from IAM API Key service
        """
        for endpoint in self.iam_endpoint:
            url = endpoint + '/oidc/jwks'
            r = requests.request('GET', url)
            if r.status_code == requests.codes.OK:
                break

        if r.status_code != requests.codes.OK:
            # IAM call failed.
            raise RuntimeError('Failed to retrieve public keys from {} with'
                               ' code {}'.format(url, r.status_code))

        keys = {}
        for key_set in r.json():
            if key_set['kty'] != 'RSA':
                # Something is wrong with the IAM response.
                raise RuntimeError('Invalid token {} returned from {}'.
                                   format(key_set, url))

            number = RSAPublicNumbers(bytes_to_long(b64decode(key_set['e'])),
                                      bytes_to_long(b64decode(key_set['n'])))
            public_key = number.public_key(default_backend())
            keys.update({
                key_set['kid']: {
                    'public_key': public_key,
                    'alg': key_set['alg']
                }
            })

        self.public_keys = keys

    def _strip_prefix(self, prefix, s):
        """
        Strip a prefix from a string.
        """
        if s.startswith(prefix):
            return s[len(prefix):]
        else:
            return s

    def _validate_iat(self, payload):
        iat = payload['iat']
        now = time()
        if iat > now:
            self.logger.warning(
                'iat is in the future by {} seconds'.format(iat - now),
                extra={
                    'message_type': 'future_iat',
                    'iat': iat,
                    'now': now,
                    'seconds_in_future': iat - now,
                },
            )
        if iat > now + API_KEY_LEEWAY:
            raise AssertionError('UNAUTHORIZED')

    def _validate_iss(self, payload):
        """
        Custom issuer validation. IAM services supports multiple regions
        Thus the the option to validate against different regions
        :param payload:
        :return:
        """

        if 'iss' not in payload:
            # MissingRequiredClaimError('iss')
            raise AssertionError('UNAUTHORIZED')

        if payload['iss'].startswith('https://iam'):
            return

        # InvalidIssuerError('Invalid issuer')
        raise AssertionError('UNAUTHORIZED')