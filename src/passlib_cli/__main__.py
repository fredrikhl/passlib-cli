#!/usr/bin/env python
# encoding: utf-8
""" Make crypt strings using `passlib`. """
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import argparse
import getpass
import itertools
import logging
import sys
import textwrap

from . import methods, parse_parameter
from . import cli_utils

logger = logging.getLogger(__name__)


def get_method(name):
    logger.debug("looking up method from name=%s", repr(name))
    m = methods[name]
    logger.debug("found method name=%s, method=%s", m.name, repr(m.method))
    return m


def get_password_loop(verify=True, allow_empty=False):
    """ Password input loop. """
    while True:
        passwd = confirm = getpass.getpass('password: ', stream=sys.stderr)
        if verify:
            confirm = getpass.getpass('confirm password: ', stream=sys.stderr)
        if passwd != confirm:
            print('Passwords does not match!', file=sys.stderr)
        elif not (passwd or allow_empty):
            print('Password is empty!', file=sys.stderr)
        else:
            return passwd


def output_columns(method_iterator):
    """ Column format methods. """
    # True/False -> yes, no
    yesno = {True: 'yes', False: 'no'}

    # Column defs (TODO: move out of this method?)
    columns = [
        ('method', lambda m: m.name),
        ('supported', lambda m: yesno[m.supported]),
        ('class', lambda m: m.class_name),
        # ('settings', lambda m: ','.join(m.settings)),
        # ('description', lambda m: m.description),
    ]

    # calculate column lengths
    c_length = [0, ] * len(columns)
    for idx in range(len(columns)):
        method_iterator, tmp_iter = itertools.tee(method_iterator)
        c_length[idx] = max(len(columns[idx][0]),
                            max(len(columns[idx][1](m)) for m in tmp_iter))

    # output method
    def row(items):
        return '  '.join('{0:{padding}}'.format(value, padding=c_length[idx])
                         for idx, value in enumerate(items))

    print(row([c[0] for c in columns]))
    print(row(['-' * cl for cl in c_length]))
    for m in method_iterator:
        print(row([c[1](m) for c in columns]))


def param_type(raw_value):
    """ Parse parameter input, e.g. foo=bar. """
    param, sep, value = raw_value.partition('=')
    if sep != '=':
        raise argparse.ArgumentTypeError(
            "invalid format ({0})".format(raw_value))
    if not param:
        raise argparse.ArgumentTypeError("empty parameter name")

    # Parse param values:
    try:
        value = parse_parameter(param, value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            "{0}, {1}".format(param, e))
    return param, value


def make_parser(supported_methods=None):
    supported_methods = supported_methods or []
    method_choices = [m.name for m in supported_methods]

    parser = argparse.ArgumentParser(
        description="Make password hashes and cryptstrings using passlib",
    )

    cli_utils.add_verbosity_mutex(parser)

    alt = parser.add_argument_group(
        'alternate actions',
        textwrap.dedent(
            """
            Options that change the default behaviour of this script.  Each
            option here will cause the script to dump some info and exit.
            """
        ).strip(),
    )
    alt_actions = alt.add_mutually_exclusive_group()
    cli_utils.add_version_arg(alt_actions)
    list_m = alt_actions.add_argument(
        '--list-methods',
        action='store_true',
        default=False,
        help="list supported methods and exit",
    )
    list_p = alt_actions.add_argument(
        '--list-params',
        action='store_true',
        default=False,
        help="list supported parameters and exit",
    )
    alt_actions.add_argument(
        '--list-all',
        action='store_true',
        default=False,
        help="list all known methods and exit",
    )
    alt_actions.add_argument(
        '--show-params',
        choices=method_choices,
        default=None,
        help="show supported parameters for %(metavar)s and exit",
        metavar='METHOD',
    )
    alt_actions.add_argument(
        '--show-docstring',
        choices=method_choices,
        default=None,
        help="show docstring for a given implementation and exit",
        metavar='METHOD',
    )

    main = parser.add_argument_group(
        'default action',
        textwrap.dedent(
            """
            The default behaviour is to ask for a password, and create a
            hash/cryptstring using the given METHOD.
            """
        ).strip(),
    )

    main.add_argument(
        '-p', '--param',
        dest='params',
        action='append',
        type=param_type,
        default=[],
        help=textwrap.dedent(
            """
            set parameters, e.g.: `-p ident=2a` or `-p rounds=12` (use {0}
            to see available)
            """
        ).format('|'.join(list_p.option_strings)).strip(),
        metavar=('PARAM=VALUE'),
    )

    main.add_argument(
        '-s', '--show-plaintext',
        dest='print_pass',
        action='store_true',
        default=False,
        help="write the plaintext password to stdout",
    )

    main.add_argument(
        '--no-verify',
        dest='verify',
        action='store_false',
        default=True,
        help="do not ask to verify password",
    )

    main.add_argument(
        'method',
        choices=method_choices,
        nargs='?',
        default='scrypt',
        help=textwrap.dedent(
            """
            hash implementation (use {0} to see available)
            """
        ).format('|'.join(list_m.option_strings)).strip(),
        metavar="METHOD",
    )
    if parser.prog == "__main__":
        parser.prog = 'python -m ' + __package__
    return parser


def main(inargs=None):
    supported_methods = [m for m in methods.values() if m.supported]
    parser = make_parser(supported_methods=supported_methods)
    args = parser.parse_args(inargs)

    cli_utils.setup_logging(args.verbosity)

    if args.list_methods:
        logger.debug("listing all supported methods")
        for m in supported_methods:
            print(m.name)
        raise SystemExit()

    if args.list_params:
        logger.debug("listing all known params")
        params = {p for m in supported_methods for p in m.settings}
        for param in sorted(params):
            print(param)
        raise SystemExit()

    if args.list_all:
        logger.debug("listing all known methods")
        output_columns(iter(methods.values()))
        raise SystemExit()

    if args.show_params:
        logger.debug("showing params for %s", repr(args.show_params))
        m = get_method(args.show_params)
        for param in sorted(m.settings):
            print(param)
        raise SystemExit()

    if args.show_docstring:
        logger.debug("showing docstring for %s", repr(args.show_docstring))
        m = get_method(args.show_docstring)
        try:
            help(m.method)
        except Exception:
            logger.warning("help() failed", exc_info=True)
            print(m.method.__doc__)
        raise SystemExit()

    logger.debug("generate using %s", repr(args.method))
    params = dict(args.params)
    method = get_method(args.method)

    if method.require_user and 'user' not in params:
        raise ValueError(
            "Method {0} requires a 'user' parameter".format(method.name))

    if method.require_password:
        try:
            password = get_password_loop(args.verify)
        except EOFError:
            raise SystemExit("EOF, abort!")
        except KeyboardInterrupt:
            raise SystemExit('Interrupt, abort!')
    else:
        password = ''

    cryptstring = method(password, **params)
    if args.print_pass:
        print(password)
    print(cryptstring)


if __name__ == '__main__':
    main()
