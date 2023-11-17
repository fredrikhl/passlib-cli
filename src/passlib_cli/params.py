# encoding: utf-8
"""
Utils for dealing with passlib parameters/settings.
"""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import logging

logger = logging.getLogger(__name__)


_parameters = dict()


def param(name):
    def register(func):
        _parameters[name] = func
        return func
    return register


def parse_parameter(parameter, value):
    if parameter not in _parameters:
        return parameter
    return _parameters[parameter](value)


@param('block_size')
@param('digest_size')
@param('hash_len')
@param('implicit_rounds')
@param('memory_cost')
@param('parallelism')
@param('rounds')
@param('salt_len')
@param('salt_size')
@param('time_cost')
def _int(input_value):
    """ integer param. """
    return int(input_value)


@param('truncate_error')
def _bool(input_value):
    """
    Boolean input value.

    Values are case-insensitive:

    - True: 1, y, yes, true
    - False: 0, n, no, false, empty value
    """
    value = input_value.strip().lower()
    if not value:
        return False
    if value in ('n', 'no', 'false', '0'):
        return False
    if value in ('y', 'yes', 'true', '1'):
        return True

    raise ValueError("invalid boolean value: " + repr(input_value))


@param('algs')
@param('ident')
@param('marker')
@param('salt')
@param('variant')
def _unmodified(input_value):
    """ raw string param. """
    return input_value
