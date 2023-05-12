# encoding: utf-8
""" CLI utils. """
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals
)

import logging

from . import metadata


LOG_FORMAT = "%(levelname)s - %(name)s - %(message)s"
LOG_LEVELS = (
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
)


def get_verbosity(verbosity):
    verbosity_idx = max(0, min(len(LOG_LEVELS) - 1, verbosity))
    return LOG_LEVELS[verbosity_idx]


def setup_logging(verbosity):
    """
    configure logging from verbosity

    :param int verbosity:
        The verbosity level from cli arguments.
    """
    if verbosity < 0:
        root = logging.getLogger()
        root.addHandler(logging.NullHandler())
    else:
        level = get_verbosity(int(verbosity))
        logging.basicConfig(format=LOG_FORMAT, level=level)


def add_verbosity_mutex(arg_parser, dest="verbosity"):
    """
    add verbosity arguments (-v, -q)

    :param arg_parser: parser or argument group
    :param str dest: name of the argument
    """
    # verbosity: -v, -vv, -vvv, -q
    log_args = arg_parser.add_mutually_exclusive_group()
    log_args.add_argument(
        "-v",
        action="count",
        dest=dest,
        help="increase verbosity (debug output/logging)",
    )
    log_args.add_argument(
        "-q",
        action="store_const",
        const=-1,
        dest=dest,
        help="silent mode - disables logging/debug output",
    )
    log_args.set_defaults(**{dest: 0})
    return log_args


def add_version_arg(arg_parser):
    """
    add a version argument (--version)

    :param arg_parser: parser or argument group
    """
    return arg_parser.add_argument(
        '--version',
        action='version',
        version='%s %s' % (metadata.package, metadata.version),
    )
