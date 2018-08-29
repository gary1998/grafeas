# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
from __future__ import unicode_literals
from collections import Mapping


CRN_FIELDS = (
    'cname',
    'ctype',
    'serviceName',
    'region',
    'scope',
    'serviceInstance',
    'resourceType',
    'resource',
)

REQUIRED_FIELDS = (
    'cname',
    'ctype',
)

SCOPE_TYPES = {
    'o': 'organizationId',
    's': 'spaceId',
    'p': 'projectId',
    'a': 'accountId',
}

SCOPE_FIELDS = {'type', 'value'}

SCOPE_TYPE_CODES = {v: k for k, v in SCOPE_TYPES.items()}

VALID_CTYPES = {
    'public',
    'dedicated',
    'local',
}


def create(fields):
    """
    Create a crn (string) from a dict of the fields.
    required fields:
        cname
        ctype
        serviceName
    optional fields:
        region
        scope
        serviceInstance
        resourceType
        resource
    scope is a dict with type and value fields.
    """
    _validate_crn_fields(fields)
    _validate_cloud_type(fields['ctype'])

    if 'scope' in fields:
        scope = fields['scope']

        if not isinstance(scope, Mapping):
            raise TypeError('scope should be a dict (or other Mapping).')

        _validate_scope_fields(scope)

        _type = scope['type']
        value = scope['value']

        if _type not in SCOPE_TYPE_CODES:
            raise ValueError(
                'Invalid scope type. (expected one of {}, got {})'
                .format(_format_iter(SCOPE_TYPE_CODES), _type)
            )
        fields = dict(fields)
        fields['scope'] = '{}/{}'.format(SCOPE_TYPE_CODES[_type], value)

    return 'crn:v1:' + ':'.join(fields.get(x, '') for x in CRN_FIELDS)


def parse(crn):
    """
    Parse a crn in to a dict of the fields.
    definite output fields:
        cname
        ctype
        serviceName
    possible output fields:
        realmid
        crn
        version
        region
        [accountID|organizationId|projectId|spaceId]
        serviceInstance
        resourceType
        resource
    Fields that are empty will be deleted from the dict.
    """

    crn_fields = crn.split(':')

    if len(crn_fields) != 10:
        raise ValueError(
            'The provided CRN has the wrong number of fields. expected {}, '
            'got {}'.format(10, len(crn_fields)),
        )

    fields = {k: v for k, v in zip(CRN_FIELDS, crn_fields[2:])}

    _validate_crn_fields(fields)
    _validate_cloud_type(fields['ctype'])

    scope = fields.get('scope')
    if scope:
        fields.update(validate_scope(scope))
        fields.pop('scope')

    crn_prefix = crn_fields[0].split('-')
    if len(crn_prefix) < 2:
        fields['crn'] = crn_fields[0]
        fields['version'] = crn_fields[1]
    else:
        fields['realmid'] = crn_prefix[0]
        fields['crn'] = crn_prefix[1]
        fields['version'] = crn_fields[1]

    for name in fields.keys():
        if not fields[name]:
            del fields[name]

    return fields


def validate_scope(scope):
    if '/' not in scope:
        raise ValueError("Missing '/' in scope.")
    scope_type_code, value = scope.split('/', 1)
    if scope_type_code not in SCOPE_TYPES:
        raise ValueError('Invalid scope type code. (expected one of {}, '
                         'got {})'.format(_format_iter(SCOPE_TYPES),
                                          scope_type_code))
    if len(value) == 0:
        raise ValueError('Empty scope value. (expected proper id)')

    return {
        SCOPE_TYPES[scope_type_code]: value
    }


def validate_cloud_type(ctype):
    _validate_cloud_type(ctype)


def _validate_cloud_type(ctype):
    if ctype not in VALID_CTYPES:
        raise ValueError('Invalid ctype. (expected one of {}, got {}'
                         .format(_format_iter(VALID_CTYPES), ctype))


def _validate_fields(fields, required, allowed, missing_msg, unknown_msg):
    for key in required:
        if not fields.get(key):
            raise ValueError(missing_msg.format(key))
    for key in fields:
        if key not in allowed:
            raise ValueError(unknown_msg.format(key))


def _validate_crn_fields(fields):
    _validate_fields(
        fields,
        REQUIRED_FIELDS,
        CRN_FIELDS,
        'Missing field {}.',
        'Unknown field {}.',
    )


def _validate_scope_fields(fields):
    _validate_fields(
        fields,
        SCOPE_FIELDS,
        SCOPE_FIELDS,
        'Missing field {} in scope.',
        'Unknown field {} in scope.',
    )


def _format_iter(iterable):
    return '[' + ', '.join(iterable) + ']'