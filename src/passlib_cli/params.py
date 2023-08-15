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
def _posint(input_value):
    return int(input_value)


@param('truncate_error')
def _bool(input_value):
    try:
        # key=1, key=0
        return bool(int(input_value))
    except ValueError:
        pass
    # key=no, key=false
    if str(input_value).lower().startswith('n'):
        return False
    if str(input_value).lower() == 'false':
        return False
    # key='' key=anything_else
    return bool(input_value)


@param('algs')
@param('salt')
@param('marker')
@param('variant')
@param('ident')
def _unmodified(input_value):
    return input_value
