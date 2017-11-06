# encoding: utf-8
""" Make crypt strings using `passlib`. """
from __future__ import absolute_import, print_function

import passlib
from collections import OrderedDict
from distutils.version import LooseVersion
from passlib.ifc import PasswordHash
from passlib.registry import list_crypt_handlers, get_crypt_handler
from passlib.utils.handlers import BackendMixin, HasUserContext, PrefixWrapper
from pkg_resources import get_distribution, DistributionNotFound


try:
    __version__ = get_distribution('passlib-crypt').version
except DistributionNotFound:
    __version__ = None


# Use the 'hash' or the 'encrypt' method of passlib.ifc.PasswordHash?
if LooseVersion(passlib.__version__) >= '1.7.0':
    PASSLIB_HASH_NAME = 'hash'
else:
    PASSLIB_HASH_NAME = 'encrypt'


def requires_password(method):
    """ Check if a the given hash implementation requires a password.

    Certain (dummy) hash implementations doesn't actually hash a password, and
    therefore doesn't need password input to generate output.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to check.

    :return bool:
        Return `True` if the implementation requires a password to hash.
    """
    return not method.is_disabled


def is_supported(method):
    """ Check if a given hash implementation is supported.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to check.

    :return bool:
        Return `True` if the method is supported.
    """
    if issubclass(method, BackendMixin):
        return method.has_backend()
    return hasattr(method, PASSLIB_HASH_NAME)


def requires_user(method):
    """ Check if a the given hash implementation requires a username.

    Username must be given to the hash method as a keyword argument, `user`.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to check.

    :return bool:
        Return `True` if the implementation requires a username parameter.
    """
    return issubclass(method, HasUserContext)


def get_description(method):
    """ Fetch a docstring usage hint from the method. """
    return getattr(method, '__doc__', '').split('\n')[0].strip()


def get_class_name(method):
    """ Get the implementation class name from a hash method.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to check.

    :return str:
        Return the module and class name as a dot-separated string.
    """

    if isinstance(method, PrefixWrapper):
        return get_class_name(method.wrapped)
    if not issubclass(method, PasswordHash):
        raise ValueError("method is not a password hash implementation")
    return '{0.__module__}.{0.__name__}'.format(method)


def make_hash(method, password, **params):
    """ Hash a password using a given implementation.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to use.

    :return str:
        Return the hash cryptstring.
    """
    return getattr(method, PASSLIB_HASH_NAME)(password, **params)


class MethodWrapper(object):
    """ method wrapper. """

    def __init__(self, method):
        self.method = method

    @property
    def name(self):
        return self.method.name

    @property
    def class_name(self):
        return get_class_name(self.method)

    @property
    def description(self):
        return get_description(self.method)

    @property
    def require_password(self):
        return requires_password(self.method)

    @property
    def require_user(self):
        return requires_user(self.method)

    @property
    def supported(self):
        return is_supported(self.method)

    def __call__(self, password, **params):
        return make_hash(self.method, password, **params)


# Init the hash mappings:
# attr_name -> MethodWrapper(attr_name, implementation_class)
methods = OrderedDict(
    (name, MethodWrapper(get_crypt_handler(name)))
    for name in list_crypt_handlers())
