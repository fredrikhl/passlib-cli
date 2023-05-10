# passlib-cli

CLI-utils for passlib.


## mkcrypt

Command line utility to make cryptstrings using [passlib].

```bash
python -m mkcrypt -p ident=2a bcrypt
```
This command will ask you to input a password using [getpass], and then output a
cryptstring, e.g.
``$2a$12$VJ8.82W/yr9acK5.i5774Ovmvme6sEanXnfbf3JWYPfVegvX4kzR.``

> This script is just an ugly wrapper that simplifies access to the hashlib
> internals. It is glued together with twigs and scotch tape.


## Install

```bash
pip install passlib
pip install <this-repo>

# Not required, but you should also…
pip install scrypt
pip install bcrypt
# … if you plan on using those backends
```


## Usage

```
usage: python -m mkcrypt [-h] [-l | --list-all | --doc METHOD] [-p PARAM=VALUE]
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
```

 [passlib]: https://passlib.readthedocs.io/en/stable/
 [getpass]: https://docs.python.org/3/library/getpass.html
