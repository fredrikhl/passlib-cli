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


def get_totp(secret):
    if secret.startswith('otpauth://'):
        return totp.TOTP.from_uri(secret)
    is_base32_like = not (set(secret) - BASE32_HINT)
    try:
        int(secret, 16)
        is_hex_like = True
    except ValueError:
        is_hex_like = False

    if is_base32_like:
        return totp.TOTP(key=secret, format='base32')
    elif is_hex_like:
        return totp.TOTP(key=secret, format='hex')

    raise ValueError('invalid secret')


def get_token(t):
    return t.generate()


parser = argparse.ArgumentParser(
    description="Generate TOTP codes using passlib",
)
parser.add_argument(
    '--live',
    action='store_true',
    help=textwrap.dedent(
        """
        Keep generating one-time passwords
        """
    ),
)
cli_utils.add_version_arg(parser)
cli_utils.add_verbosity_mutex(parser)


def main(inargs=None):
    args = parser.parse_args(inargs)
    cli_utils.setup_logging(args.verbosity)

    secret = sys.stdin.readline().rstrip()
    generator = get_totp(secret)

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
