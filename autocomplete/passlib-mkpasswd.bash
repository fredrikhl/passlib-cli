function _mkcrypt_autocomplete {
    local methods curr
    local -a opts
    methods="$(passlib-mkpasswd --list-methods)"
    curr="${COMP_WORDS[$COMP_CWORD]}"

    # TODO: Implement some way of fetching these from mkcrypt
    opts=("-h" "--help" "-v" "--verbose" "--version" \
          "--list-methods" "--list-params" "--list-all" \
          "--show-params" "--show-docstring" \
          "-p" "--param" \
          "-s" "--show-plaintext" "--no-verify")

    COMPREPLY=()

    if [[ "$curr" == -* ]];
    then
        COMPREPLY=( $(compgen -W "${opts[*]}" -- "$curr") )
    elif [ "${COMP_CWORD}" -gt 1 ] && [ "${COMP_WORDS[$COMP_CWORD-1]}" == "-p" ];
    then
        # TODO: Implement some way of fetching known/valid settings from mkcrypt
        COMPREPLY=()
    else
        COMPREPLY=( $(compgen -W "$methods" -- "$curr") )
    fi
}

complete -F _mkcrypt_autocomplete passlib-mkpasswd
