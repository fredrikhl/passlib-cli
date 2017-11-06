#!/usr/bin/env python
# encoding: utf-8
""" Make crypt strings using `passlib`. """
from __future__ import absolute_import, print_function
import argparse
import getpass
import sys
from functools import partial
from mkcrypt import methods, __version__


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


def output_all():
    """ List methods (columns: name, supported, class, description) """
    # column headers
    name_hdr = 'method'
    cls_hdr = 'class'
    impl_hdr = 'supported'
    desc_hdr = 'description'

    # columns value map
    impl_map = {True: 'yes', False: 'no'}

    # column widths
    name_len = max(len(name_hdr), max(len(n) for n in methods))
    cls_len = max(len(cls_hdr),
                  max(len(m.class_name) for m in methods.values()))
    impl_len = max(len(impl_hdr), max(len(v) for v in impl_map.values()))
    desc_len = max(len(desc_hdr), max(len(m.description)
                                      for m in methods.values()))

    row = partial('{0:{w0}}  {1:{w1}}  {2:{w2}}  {3:{w3}}'.format,
                  w0=name_len, w1=impl_len, w2=cls_len, w3=desc_len)

    print(row(name_hdr, impl_hdr, cls_hdr, desc_hdr))
    print(row('-' * name_len, '-' * impl_len, '-' * cls_len, '-' * desc_len))
    for m in methods.values():
        print(row(m.name, impl_map[m.supported], m.class_name, m.description))


PARAM_MAP = {
    'salt_size': int,
    'rounds_cost': int,
    'rounds': int,
}


def param_type(key_value):
    """ Parse parameter input, e.g. foo=bar. """
    key, sep, value = key_value.partition('=')
    if sep != '=':
        raise argparse.ArgumentTypeError(
            "invalid format ({0})".format(key_value))
    if not key:
        raise argparse.ArgumentTypeError("empty parameter")

    # Parse int params:
    try:
        if key in PARAM_MAP:
            value = PARAM_MAP[key](value)
        elif not value:
            raise ValueError("empty value ('{0}')".format(value))
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            "invalid '{0}' value: {1}".format(key, e))
    return key, value


def main(args=None):
    supported_methods = [m.name for m in methods.values() if m.supported]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=__version__)

    and_exit = parser.add_mutually_exclusive_group()
    ls = and_exit.add_argument(
        '-l', '--list',
        action='store_true',
        default=False,
        help="list supported methods and exit")
    and_exit.add_argument(
        '--list-all',
        action='store_true',
        default=False,
        help="list all known methods and exit")
    and_exit.add_argument(
        '--doc',
        choices=supported_methods,
        metavar='METHOD',
        default=None,
        help="show docstring for a given implementation and exit")

    # TODO: type=param_type or nargs=2?
    parser.add_argument(
        '-p',
        dest='params',
        action='append',
        type=param_type,
        metavar=('PARAM=VALUE'),
        default=[],
        help=("set parameters,"
              " e.g.: `-p ident=2a` or `-p rounds=12`"))

    parser.add_argument(
        '-s', '--show-plaintext',
        dest='print_pass',
        action='store_true',
        default=False,
        help="write the plaintext password to stdout")

    parser.add_argument(
        '--no-verify',
        dest='verify',
        action='store_false',
        default=True,
        help="do not ask to verify password")

    parser.add_argument(
        'crypt',
        choices=supported_methods,
        metavar='METHOD',
        nargs='?',
        default='scrypt',
        help="hash implementation (use {0} to see"
             " available)".format('|'.join(ls.option_strings)))

    # TODO: rounds, salt, rounds_cost, salt_size?

    args = parser.parse_args()

    if args.list:
        for name in supported_methods:
            print(name)
        raise SystemExit()

    if args.list_all:
        output_all()
        raise SystemExit()

    if args.doc:
        m = methods[args.doc]
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
    main()
