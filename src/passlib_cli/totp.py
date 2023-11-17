#!/usr/bin/env python
# encoding: utf-8
""" TOTP CLI utils. """
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import argparse
import logging
import string
import sys
import textwrap
import time

from passlib import totp

from . import cli_utils

logger = logging.getLogger(__name__)

BASE32_HINT = set(string.ascii_uppercase + '234567')


def could_be_base32(value):
    return not (set(value) - BASE32_HINT)


def could_be_hex(value):
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def get_totp(secret, fmt=None):
    """ parse totp input secret. """
    logger.debug("totp format: %r", repr(fmt) if fmt else "auto")
    if fmt == 'uri' or (not fmt and secret.startswith('otpauth://')):
        return totp.TOTP.from_uri(secret)

    if fmt == 'base32' or (not fmt and could_be_base32(secret)):
        return totp.TOTP(key=secret, format='base32')

    if fmt == 'hex' or (not fmt and could_be_hex(secret)):
        return totp.TOTP(key=secret, format='hex')

    raise ValueError('invalid secret')


def format_totp(obj, fmt=None):
    """ format totp secret. """
    if fmt == 'base32':
        return obj.base32_key
    if fmt == 'hex':
        return obj.hex_key
    return obj.to_uri()


def get_token(t):
    return t.generate()


parser = argparse.ArgumentParser(
    description="Generate TOTP codes using passlib",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument(
    '--live',
    action='store_true',
    help=textwrap.dedent(
        """
        Keep generating one-time passwords
        """
    ).strip(),
)
fmt_args = parser.add_argument_group(
    "secret format",
    textwrap.dedent(
        """
        Set the format for the shared secret input.  The format is guessed if
        not given.

        If a new secret is generated, this controls the output format.  If
        generating a new uri formatted secret (the default), you *must* provide
        a label.
        """
    ).strip()
)
fmt_mutex = fmt_args.add_mutually_exclusive_group()
fmt_mutex.add_argument(
    "--uri",
    action="store_const",
    dest="fmt",
    const="uri",
)
fmt_mutex.add_argument(
    "--base32",
    action="store_const",
    dest="fmt",
    const="base32",
)
fmt_mutex.add_argument(
    "--hex",
    action="store_const",
    dest="fmt",
    const="hex",
)
not_set = object()
label_arg = parser.add_argument(
    "--new",
    dest="label",
    nargs="?",
    default=not_set,
    help="create and print a new TOTP secret",
    metavar="label"
)
cli_utils.add_version_arg(parser)
cli_utils.add_verbosity_mutex(parser)


def main(inargs=None):
    args = parser.parse_args(inargs)
    cli_utils.setup_logging(args.verbosity)

    if args.label is not_set:
        # read totp secret from stdin
        secret = sys.stdin.readline().rstrip()
        generator = get_totp(secret, fmt=args.fmt)
    else:
        # generate new totp secret
        if (args.fmt == "uri" or not args.fmt) and not args.label:
            err = argparse.ArgumentError(
                label_arg,
                "missing label for new uri formatted secret",
            )
            parser.error(str(err))
        generator = totp.TOTP(new=True, label=args.label)
        print(format_totp(generator, fmt=args.fmt))

    def needs_wait(token):
        return token.expire_time - time.time()

    while True:
        token = get_token(generator)
        print(token.token)

        if args.live:
            while (tleft := needs_wait(token)) > 0:
                logger.debug("time left: %d", tleft)
                # sleep for one second at a time to catch e.g.
                # KeyboardInterrupts
                time.sleep(1)
            continue
        else:
            break


if __name__ == '__main__':
    parser.prog = 'python -m ' + __spec__.name
    main()
