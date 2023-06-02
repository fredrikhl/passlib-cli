# passlib-cli

CLI-utils to simplify access to passlib crypt methods. It is glued together
with twigs and scotch tape.


## passlib-mkpasswd

Command line utility to make cryptstrings and password hashes using [passlib].

```bash
passlib-mkpasswd -p ident=2a bcrypt
python -m passlib_cli -p ident=2a bcrypt
```

This command will ask you to input a password using [getpass], and then output a
cryptstring, e.g.
``$2a$12$VJ8.82W/yr9acK5.i5774Ovmvme6sEanXnfbf3JWYPfVegvX4kzR.``


## passlib-autocomplate

Generates autocomplete script for *bash*:

```bash
source <(passlib-autocomplete)
```


## passlib-totp

Generates one time passwords from a TOTP shared secret, or an `otpauth://` uri:

```bash
echo ABCDEFGHIJ234567 | passlib-totp
echo otpauth://totp/example.org:user@example.org?secret=ABCDEFGHIJ234567 | passlib-totp
```


## Install

```bash
pip install <this-repo>

# Not required, but you should also…
pip install scrypt
pip install bcrypt
# … if you plan on using those backends
```


## Usage

```
usage: passlib-mkpasswd [-h] [-l | --list-all | --doc METHOD] [-p PARAM=VALUE]
                         [-s] [--no-verify] [METHOD]

positional arguments:
  METHOD                hash implementation (use -l|--list to see available)

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list supported methods and exit
  --list-all            list all known methods and exit
  --doc METHOD          show docstring for a given implementation and exit
  -p PARAM=VALUE        set parameters, e.g.: `-p ident=2a` or `-p rounds=12`
                        Using `--doc METHOD' will usually give some details on
                        available parameters.
  -s, --show-plaintext  write the plaintext password to stdout
  --no-verify           do not ask to verify password


usage: passlib-mkpasswd [-h] [-v]
                        [--version | --list-methods | --list-params |
                         --list-all | --show-params METHOD |
                         --show-docstring METHOD]
                        [-p PARAM=VALUE] [-s] [--no-verify] [METHOD]

options:
  -h, --help            show this help message and exit
  -v, --verbose         enable/increase output verbosity

alternate actions:
  Options that change the default behaviour of this script. Each option here
  will cause the script to dump some info and exit.

  --version             show program's version number and exit
  --list-methods        list supported methods and exit
  --list-params         list supported parameters and exit
  --list-all            list all known methods and exit
  --show-params METHOD  show supported parameters for METHOD and exit
  --show-docstring METHOD
                        show docstring for a given implementation and exit

make crypt:
  -p PARAM=VALUE, --param PARAM=VALUE
                        set parameters, e.g.: `-p ident=2a` or `-p rounds=12`
                        (use ['--list-params'] to see available)
  -s, --show-plaintext  write the plaintext password to stdout
  --no-verify           do not ask to verify password
  METHOD                hash implementation (use --list-methods to see
                        available)

```

 [passlib]: https://passlib.readthedocs.io/en/stable/
 [getpass]: https://docs.python.org/3/library/getpass.html
