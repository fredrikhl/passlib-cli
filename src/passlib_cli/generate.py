#!/usr/bin/env python
# encoding: utf-8
""" Password generator cli util. """
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import argparse
import logging
import textwrap

from passlib import pwd

from . import cli_utils

logger = logging.getLogger(__name__)


default_phrase_sep = "-"
default_word_charset = "ascii_72"


def generate_passphrase(entropy=None, length=None, sep=default_phrase_sep):
    params = {
        'entropy': entropy,
        'length': length,
        'sep': sep,
    }
    logger.info("generating passphrase using %s", repr(params))
    return pwd.genphrase(**params)


def generate_password(entropy=None, length=None, charset=default_word_charset):
    params = {
        'entropy': entropy,
        'length': length,
        'charset': charset,
    }
    logger.info("generating password using %s", repr(params))
    return pwd.genword(**params)


parser = argparse.ArgumentParser(
    description="Generate plaintext passwords using passlib.pwd",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

default_type = "genword"
type_mutex = parser.add_mutually_exclusive_group()
type_mutex.add_argument(
    "--random",
    action="store_const",
    const="genword",
    dest="type",
    help=(
        "Generate a random string" +
        (" (default)" if default_type == "genword" else "")
    ),
)
type_mutex.add_argument(
    "--phrase",
    action="store_const",
    const="genphrase",
    dest="type",
    help=(
        "Generate a passphrase" +
        (" (default)" if default_type == "genphrase" else "")
    ),
)
type_mutex.set_defaults(type=default_type)

params_group = parser.add_argument_group(
    "Parameters",
    textwrap.dedent(
        """
        Parameters for the password generator.

        Note that some parameters only applies to passwords or passphrases.

        If both entropy and length is given, the stronger will be used.
        Entropy can be given as a numerical value, or as a preset.  Valid
        presets are: "weak" (24), "fair" (36), "strong" (48), "secure" (56).
        """
    ).lstrip(),
)


def entropy_type(value):
    if value.isdigit():
        return int(value)
    return value


params_group.add_argument(
    "--entropy",
    default=None,
    type=entropy_type,
    help="Generate a password of (minimum) strength %(metavar)s",
    metavar="E",
)

params_group.add_argument(
    "--length",
    type=int,
    default=None,
    help="Generate a password of (at least) %(metavar)s characters",
    metavar="N",
)

params_group.add_argument(
    "--sep",
    default=default_phrase_sep,
    help=(
        "For passphrase: use %(metavar)s as word separator " +
        "(default: %(default)s)"
    ),
    metavar="D",
)

cli_utils.add_version_arg(parser)
cli_utils.add_verbosity_mutex(parser)


def main(inargs=None):
    args = parser.parse_args(inargs)
    cli_utils.setup_logging(args.verbosity)

    if args.type == "genphrase":
        generate = generate_passphrase
        params = {
            'sep': args.sep,
        }
    else:
        generate = generate_password
        params = {
            'charset': default_word_charset,
        }
    params.update({
        'entropy': args.entropy,
        'length': args.length,
    })
    print(generate(**params))


if __name__ == '__main__':
    parser.prog = 'python -m ' + __spec__.name
    main()
