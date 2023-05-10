#!/usr/bin/env python
# encoding: utf-8
""" Make crypt strings using `passlib`. """
from __future__ import absolute_import, print_function
import argparse
import logging
import getpass
import sys
from itertools import tee as iter_tee
from . import methods, parse_parameter, __version__

logger = logging.getLogger(__name__)

verbosity_levels = [
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
]


def set_verbosity(verbosity):
    try:
        level = verbosity_levels[verbosity]
    except IndexError:
        level = logging.DEBUG
    logging.getLogger().setLevel(level)


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
        method_iterator, tmp_iter = iter_tee(method_iterator)
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

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        help="enable/increase output verbosity")

    alt = parser.add_argument_group('alternate actions',
                                    'Options that change the default '
                                    'behaviour of this script. '
                                    'Each option here will cause the script '
                                    'to dump some info and exit')
    alt_actions = alt.add_mutually_exclusive_group()
    alt_actions.add_argument(
        '--version',
        action='version',
        version=__version__)
    list_m = alt_actions.add_argument(
        '--list-methods',
        action='store_true',
        default=False,
        help="list supported methods and exit")
    list_p = alt_actions.add_argument(
        '--list-params',
        action='store_true',
        default=False,
        help="list supported parameters and exit")
    alt_actions.add_argument(
        '--list-all',
        action='store_true',
        default=False,
        help="list all known methods and exit")
    alt_actions.add_argument(
        '--show-params',
        choices=method_choices,
        metavar='METHOD',
        default=None,
        help="show supported parameters for %(metavar)s and exit")
    alt_actions.add_argument(
        '--show-docstring',
        choices=method_choices,
        metavar='METHOD',
        default=None,
        help="show docstring for a given implementation and exit")

    main = parser.add_argument_group('make crypt')

    main.add_argument(
        '-p', '--param',
        dest='params',
        action='append',
        type=param_type,
        metavar=('PARAM=VALUE'),
        default=[],
        help=("set parameters,"
              " e.g.: `-p ident=2a` or `-p rounds=12`"
              " (use {0} to see available)".format(list_p.option_strings)))

    main.add_argument(
        '-s', '--show-plaintext',
        dest='print_pass',
        action='store_true',
        default=False,
        help="write the plaintext password to stdout")

    main.add_argument(
        '--no-verify',
        dest='verify',
        action='store_false',
        default=True,
        help="do not ask to verify password")

    main.add_argument(
        'crypt',
        choices=method_choices,
        metavar='METHOD',
        nargs='?',
        default='scrypt',
        help="hash implementation (use {0} to see"
             " available)".format('|'.join(list_m.option_strings)))
    return parser


def main(inargs=None):
    supported_methods = [m for m in methods.values() if m.supported]
    parser = make_parser(supported_methods=supported_methods)
    args = parser.parse_args(inargs)

    if args.verbose:
        set_verbosity(args.verbose)

    logger.debug('args: {0}'.format(repr(args)))

    if args.list_methods:
        for m in supported_methods:
            print(m.name)
        raise SystemExit()

    if args.list_params:
        params = {p for m in supported_methods for p in m.settings}
        for param in sorted(params):
            print(param)
        raise SystemExit()

    if args.list_all:
        output_columns(iter(methods.values()))
        raise SystemExit()

    if args.show_params:
        m = methods[args.show_params]
        for param in sorted(m.settings):
            print(param)
        raise SystemExit()

    if args.show_docstring:
        m = methods[args.show_docstring]
        help(m.method)
        raise SystemExit()

    params = dict(args.params)
    method = methods[args.crypt]

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
    logging.basicConfig(format="%(levelname)s - %(name)s - %(message)s",
                        level=verbosity_levels[0],
                        stream=sys.stderr)
    main()
