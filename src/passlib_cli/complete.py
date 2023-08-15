#!/usr/bin/env python
# encoding: utf-8
"""
Autocomplete utils.
"""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import argparse
import logging
import shlex

from . import methods
from . import cli_utils

logger = logging.getLogger(__name__)


OPTIONS = (
    "--list-all",
    "--list-methods",
    "--list-params",
    "--no-verify",
    "--show-docstring",
    "--show-params",
    "--version",
    "-h", "--help",
    "-p", "--param",
    "-s", "--show-plaintext",
    "-v", "--verbose",
)


template = """
_mkcrypt_autocomplete()
{{
    local curr
    local -a methods opts

    curr="${{COMP_WORDS[$COMP_CWORD]}}"
    methods=( {methods} )
    opts=( {options} )

    COMPREPLY=()

    if [[ "$curr" == -* ]];
    then
        COMPREPLY=( $(compgen -W "${{opts[*]}}" -- "$curr") )
    elif [ "${{COMP_CWORD}}" -gt 1 ] \\
          && [ "${{COMP_WORDS[$COMP_CWORD-1]}}" == "-p" ];
    then
        # TODO: Implement fetching known/valid settings from mkcrypt
        COMPREPLY=()
    else
        COMPREPLY=( $(compgen -W "${{methods[*]}}" -- "$curr") )
    fi
}}

complete -F _mkcrypt_autocomplete passlib-mkpasswd
"""


def format_text_list(items):
    return " ".join(shlex.quote(item) for item in items)


def format_autocomplete_script(methods):
    return template.format(
        options=format_text_list(OPTIONS),
        methods=format_text_list(methods),
    )


def main(inargs=None):
    parser = argparse.ArgumentParser(
        description="Make autocomplete bash script for passlib",
    )

    cli_utils.add_verbosity_mutex(parser)
    cli_utils.add_version_arg(parser)
    args = parser.parse_args(inargs)

    cli_utils.setup_logging(args.verbosity)

    supported_methods = [m for m in methods.values() if m.supported]
    method_list = [m.name for m in supported_methods]

    # m = methods[args.show_params]
    # for param in sorted(m.settings):
    #     print(param)

    script = format_autocomplete_script(method_list)
    print(script)


if __name__ == '__main__':
    main()
